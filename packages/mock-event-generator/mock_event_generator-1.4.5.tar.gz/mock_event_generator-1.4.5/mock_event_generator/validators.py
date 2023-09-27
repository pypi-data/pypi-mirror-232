"""Classes for G-event and S-event validation."""

from __future__ import annotations

import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import astropy
import astropy.coordinates
import astropy.time
import matplotlib.pyplot as plt  # type: ignore[attr-defined]
import mocpy
import numpy as np
from matplotlib import colormaps  # type: ignore[attr-defined]
from requests import HTTPError

from .analize_utils import (
    AnalizeLogsSuperEvents,
    AnalizePipelinesSEvents,
    is_significant,
    should_publish,
)
from .cache import GEventCacheEntry, SEventCacheEntry
from .exceptions import MEGValidationFailed
from .gracedbs import GraceDBWithContext

# import astropy_healpix
# import healpy
# import mocpy


logger = logging.getLogger(__name__)

# Files and Labels that should be present for MDC test event checklist

FILES_CHECKLIST_MDC = [
    'bayestar.multiorder.fits',
    'bayestar.fits.gz',
    'bayestar.png',
    'bayestar.volume.png',
    'bayestar.html',
    '{}.p_astro.json',
    '{}.p_astro.png',
    'em_bright.json',
    'em_bright.png',
]

LABELS_CHECKLIST_MDC = [
    'EMBRIGHT_READY',
    'GCN_PRELIM_SENT',
    'PASTRO_READY',
    'SKYMAP_READY',
    'DQR_REQUEST',
]

ADV_LABELS = ['ADVNO', 'ADVOK', 'ADVREQ']


class SEventValidator(SEventCacheEntry):
    """Class used to validate a cached S-event."""

    datetime_format = '%Y-%m-%d %H:%M:%S %Z'
    cmap = colormaps['tab10']
    data_template = {'found': False, 'time': 'never', 'latency': 9999.0}
    loginfo = True

    @classmethod
    def from_sevent_id(
        cls,
        sevent_id: str,
        source: GraceDBWithContext,
        disabled: bool,
        cache_path: Path,
    ) -> SEventValidator:
        """Init from S-event id.

        Fetches S-event and returns a validator instance.

        Parameters:
            sevent_id: The S-event GraceDB identifier.
            source: The GraceDB instance name from which events are downloaded,
                such as `production` or `playground`.
            disabled: If true, bypass the cache and always download the event
                data files.
            cache_path: The top-level path of the cache.
        """
        SEventCacheEntry.from_id(sevent_id, source, disabled, cache_path)

        return SEventValidator(cache_path / sevent_id)

    @classmethod
    def from_gevent_id(
        cls,
        gevent_id: str,
        source: GraceDBWithContext,
        disabled: bool,
        cache_path: Path,
    ) -> SEventValidator:
        """Init from G-event id.

        Fetches G-event info, queries for S-events in the corresponding
        search and returns a validator instance for the S-event associated to
        the input G-event.

        Parameters:
            gevent_id: The G-event GraceDB identifier.
            source: The GraceDB instance name from which events are downloaded,
                such as `production` or `playground`.
            disabled: If true, bypass the cache and always download the event
                data files.
            cache_path: The top-level path of the cache.

        Raises:
            RuntimeError: When the input G-event does not have ans associated
                S-event.
        """
        gevent_data = GEventCacheEntry.from_id(
            gevent_id, source, disabled, cache_path
        ).get_description()
        sevent_id = gevent_data.superevent

        return SEventValidator.from_sevent_id(sevent_id, source, disabled, cache_path)

    def _get_labels(self) -> dict[str, Any]:
        """Load labels info into a dictionary."""
        logs = self.sevent_data['labels']
        labels_dict = {
            key: self.data_template.copy() for key in LABELS_CHECKLIST_MDC + ADV_LABELS
        }
        for row in logs:
            labelname = row['name']
            log_time = datetime.strptime(row['created'], self.datetime_format)
            # logger.info(f'Label {labelname} created {str(log_time)}')
            if labelname in LABELS_CHECKLIST_MDC + ADV_LABELS:
                labels_dict[labelname]['found'] = True
                labels_dict[labelname]['time'] = str(log_time)
                labels_dict[labelname]['latency'] = (
                    log_time - self.sub_time
                ).total_seconds()

        return labels_dict

    def _get_files(self) -> dict[str, Any]:
        """Load files info into a dictionary."""
        logs = self.sevent_data['logs']['log']
        files_dict = {
            key.format(self.pipeline): self.data_template.copy()
            for key in FILES_CHECKLIST_MDC
        }
        for row in logs:
            filename = row['filename']
            log_time = datetime.strptime(row['created'], self.datetime_format)
            if filename:
                pass
                # logger.info(f'File {filename} created {str(log_time)}')
            if filename in files_dict:
                files_dict[filename]['found'] = True
                files_dict[filename]['time'] = str(log_time)
                files_dict[filename]['latency'] = (
                    log_time - self.sub_time
                ).total_seconds()

        return files_dict

    def _get_file_dataproduct_ev(
        self, filename: str, ev: str, filename_path: Path
    ) -> bytes:
        """Get content of a files from the cache.

        Parameters:
            ev: The event GraceDB identifier.
            filename: The name of the file to download
            filename_path: The path to the cached file.
        """
        if filename_path.exists():
            filename_data = filename_path.read_bytes()
        else:
            source = GraceDBWithContext.meg_from_alias_or_url(
                self.get_description().source
            )
            try:
                response = source.files(ev, filename)
            except HTTPError as exc:
                if exc.response.status != 404:
                    raise
                raise ValueError(f'Event {ev}: File {filename!r} not found.')
            print(f'Event {ev}: File {filename!r} found!')
            filename_data = response.read()
            filename_path.write_bytes(filename_data)

        return filename_data

    def _get_sevent_data_and_history(self) -> None:
        """Create data entry in the SEventValidator class.

        Return:
        -  self.history_properties  : [kind][ [latency,description,log] ....]
        -  self.history_alerts      : [kind][ [latency,type,file,vers,log#] ....]
        -  self.history_dataproducts: [kind][ [latency,file,vers,comment,log#] ...]
        -  self.dataproducts        : (binary) of dataproductw [kind]['filename,vers']
        -  self.dataalerts          : (binary) of alerts       [kind]['filename,vers']
        -  self.datalocalizations   : (binary) of events localizations [GEV]
        -  self.labels_dict         : to be removed used for MDC checklist
        -  self.files_dict          : to be removed used for MDC checklist
        """
        # Get list of files and label in MDC checklist
        self.labels_dict = self._get_labels()
        self.files_dict = self._get_files()

        # Get history of S-event
        history_data = AnalizeLogsSuperEvents(self.sevent_data['logs']['log'], self.t_0)
        self.history_properties = history_data[0]
        self.history_alerts = history_data[1]
        self.history_dataproducts = history_data[2]
        # Get properties G-events and groups
        self.group_events, self.group_fars = AnalizePipelinesSEvents(
            self.sevent_data['sevent'], self.sevent_data['gevents'], log=False
        )

        # GET DATA PRODUCTS
        self.dataproducts: dict[str, Any] = dict()
        for dataproduct in self.history_dataproducts:
            self.dataproducts[dataproduct] = dict()
            dataproducts = self.history_dataproducts[dataproduct]
            for elem in dataproducts:
                filename = elem[1] + ',' + str(elem[2])
                filename_path = self.path / filename
                filename_data = self._get_file_dataproduct_ev(
                    filename, self.sevent_id, filename_path
                )
                self.dataproducts[dataproduct][filename] = filename_data

        # GET DATA ALERTS
        self.dataalerts: dict[str, Any] = dict()
        for dataproduct in self.history_alerts:
            self.dataalerts[dataproduct] = dict()
            dataproducts = self.history_alerts[dataproduct]
            for elem in dataproducts:
                filename_alert = elem[2]
                filename_path = self.path / filename_alert
                filename_data = self._get_file_dataproduct_ev(
                    filename_alert, self.sevent_id, filename_path
                )
                self.dataalerts[dataproduct][filename_alert] = filename_data

        # GET EVENTS LOCALIZATIONS
        self.datalocalizations: dict[str, Any] = dict()
        for gev_id in self.sevent_data['sevent']['gw_events']:
            data_event = self.sevent_data['gevents'][gev_id]
            group_event = data_event['group'].lower()
            pipeline_event = data_event['pipeline'].lower()
            labels_event = data_event['labels']
            try:
                if group_event == 'cbc' and 'SKYMAP_READY' in labels_event:
                    localization = 'bayestar.multiorder.fits,0'
                    filename_path = self.path / gev_id / localization
                    filename_data = self._get_file_dataproduct_ev(
                        localization, gev_id, filename_path
                    )
                elif group_event == 'burst' and 'SKYMAP_READY' in labels_event:
                    localization = pipeline_event + '.multiorder.fits,0'
                    filename_path = self.path / gev_id / localization
                    filename_data = self._get_file_dataproduct_ev(
                        localization, gev_id, filename_path
                    )
                else:
                    filename_data = b''
            except ValueError:
                logger.info(
                    f'Event {gev_id} is invalid. No localization file {localization}'
                )
                filename_data = b''
            self.datalocalizations[gev_id] = filename_data

    def validate(self, save_plot_to: Path | None) -> None:
        """Superevent validation method.

        Get S-event description, recover labels and file info,
        validate and produce a plot.

        Raises:
            RuntimeError: When the validation fails.
        """
        self.sevent_data = self.get_description().sevent_data
        self.sevent_id = self.sevent_data['sevent']['superevent_id']
        self.t_0 = self.sevent_data['sevent']['t_0']
        self.sub_time = datetime.strptime(
            self.sevent_data['sevent']['created'], self.datetime_format
        )
        logger.info(
            'Validating {} submitted {} from graceDB {}'.format(
                self.sevent_id, str(self.sub_time), str(self.get_description().source)
            )
        )

        # GET SEVENT MAIN PRODUCTS
        self.sev_values = self.sevent_data['sevent']
        self.gev_values = self.sevent_data['sevent']['preferred_event_data']
        self.group = self.gev_values['group'].lower()
        self.pipeline = self.gev_values['pipeline'].lower()
        self.search = self.gev_values['search'].lower()
        self.superevent_id = self.sev_values['superevent_id']
        self.is_significant = is_significant(self.gev_values)
        self.is_earlywaring = 'EARLY_WARNING' in self.sevent_data['sevent']['labels']
        self.is_raven = 'RAVEN_ALERT' in self.sevent_data['sevent']['labels']
        self.is_cbc = (
            'cbc' == self.sevent_data['sevent']['preferred_event_data']['group'].lower()
        )
        self.is_mdc = (
            'mdc'
            == self.sevent_data['sevent']['preferred_event_data']['search'].lower()
        )
        self.should_publish = should_publish(self.gev_values)

        logger.info(f'Event {self.sevent_id} is_significant is {self.is_significant}')
        logger.info(f'Event {self.sevent_id} should_publish is {self.should_publish}')
        logger.info(f'Event {self.sevent_id} is cbc {self.is_cbc}')
        logger.info(f'Event {self.sevent_id} is mdc {self.is_mdc}')
        logger.info(f'Event {self.sevent_id} is EARLY_WARNING {self.is_earlywaring}')
        logger.info(f'Event {self.sevent_id} is RAVEN {self.is_raven}')

        # Get SEVENT data and history
        self._get_sevent_data_and_history()

        # #################################
        # Perform validation checks
        # #################################

        validation_tests: list[str] = []

        # TESTs thae advocate action are requests
        if self.is_significant:
            validation_tests = validation_tests + self._validate_advocate()

        # Checks that apply to CBC Alerts (From MDC checklist)
        if self.should_publish and self.is_cbc and not self.is_earlywaring:
            validation_tests = validation_tests + self._validate_labels()
            validation_tests = validation_tests + self._validate_files()
        else:
            logger.info(
                f'Event {self.sevent_id} validation of LABELS and FILES not performed.'
            )

        count_prelimary_alerts = dict()
        for kind in self.history_alerts:
            count_prelimary_alerts[kind] = 0
            for alert in self.history_alerts[kind]:
                if alert[1] == 'preliminary':
                    count_prelimary_alerts[kind] += 1
        logger.info(
            f'Event {self.sevent_id} #of Preliminary is: {count_prelimary_alerts}'
        )
        # Check that we have at least two prelimary in case of
        # alerts that are not EarlyWarning
        if (
            count_prelimary_alerts['xml'] < 2
            and self.should_publish
            and (not self.is_earlywaring)
        ):
            validation_tests = validation_tests + [
                'Number of XML preliminary alert is {} (less than two).'.format(
                    count_prelimary_alerts['xml']
                )
            ]

        # Ouput infos to the appropriate files
        if not save_plot_to:
            save_plot_to = self.path

        self._save_analize_sev_history(save_plot_to)
        self._save_data(save_plot_to)
        self._plot(save_plot_to)

        if len(validation_tests) > 0:
            err_str = f'Validation failed for S-event {self.sevent_id}\n'
            for validation_test in validation_tests:
                err_str = err_str + validation_test + '\n'
            raise MEGValidationFailed(err_str)

    def _validate_labels(self) -> list[str]:
        """Returns True if all labels are found."""
        validation = []
        for key in LABELS_CHECKLIST_MDC:
            if not self.labels_dict[key]['found']:
                validation.append(f'Missing labels: {key}')
        return validation

    def _validate_advocate(self) -> list[str]:
        """Returns True if advocate label (either ADVOK, ADVNO or ADV_REQ) is found."""
        adv_created = [self.labels_dict[key]['found'] for key in ADV_LABELS]
        if any(adv_created):
            validation = []
        else:
            validation = [f'Missing ADV label (either one of {ADV_LABELS}).']
        return validation

    def _validate_files(self) -> list[str]:
        """Returns True if all filenames are found."""
        validation = []
        for key in self.files_dict:
            if not self.files_dict[key]['found']:
                validation.append(f'Missing File: {key}')
        return validation

    def _save_data(self, outdir: Path) -> None:
        """Saves latency data to json files..

        Parameters:
            outdir: Output directory.
        """
        data_dict = {
            'sub_time': str(self.sub_time),
            'labels': self.labels_dict,
            'files': self.files_dict,
            'superevent_id': self.sevent_id,
            't_0': self.t_0,
            'history_properties': self.history_properties,
            'history_alerts': self.history_alerts,
            'history_dataproducts': self.history_dataproducts,
            'sev_data': self.sevent_data,
        }
        filename = outdir / ('%s_latency_data.json' % str(self.sevent_id))
        with open(filename, 'w') as stream:
            json.dump(data_dict, stream, indent=4)
        logger.info(f'Data saved to {str(filename)}')

    def _plot(self, outdir: Path) -> None:
        """Plots timeline of label and filename creation.

        Parameters:
            outdir: Output directory.
        """
        self._init_figure()
        self._add_entries_to_plot(self.axes[0], self.labels_dict)
        self._add_entries_to_plot(self.axes[1], self.files_dict)

        x_span = (
            self.axes[1].get_xlim()[1]  # type: ignore[attr-defined]
            - self.axes[1].get_xlim()[0]  # type: ignore[attr-defined]
        )  # type: ignore[attr-defined]
        self.axes[1].set_xlim(  # type: ignore[attr-defined]
            self.axes[1].get_xlim()[0],  # type: ignore[attr-defined]
            self.axes[1].get_xlim()[1] + 0.2 * x_span,  # type: ignore[attr-defined]
        )
        textstr = ''
        for key in ['superevent_id', 'category', 'submitter', 'created', 't_0']:
            textstr += '{}: {}\n'.format(key, self.sevent_data['sevent'][key])
        self.axes[1].text(  # type: ignore[attr-defined]
            0.01,
            0.05,
            textstr[:-2],
            fontsize=10,
            transform=self.axes[1].transAxes,  # type: ignore[attr-defined]
            va='bottom',
            ha='left',
            bbox={'boxstyle': 'round', 'facecolor': 'white', 'alpha': 0.6},
        )

        plt.tight_layout()  # type: ignore[attr-defined]
        plt.subplots_adjust(hspace=0)

        filename = outdir / ('%s_latency_plot.png' % str(self.sevent_id))
        plt.savefig(filename)
        logger.info(f'Plot saved to {str(filename)}')

    def _init_figure(self) -> None:
        """Init matplotlib objects."""
        plt.rc('font', size=10)  # type: ignore[attr-defined]
        self.fig = plt.figure(figsize=(10, 5))
        self.axes = []

        self.axes.append(self.fig.add_subplot(2, 1, 1))
        self.axes[0].grid(ls='--')  # type: ignore[call-arg]
        self.axes[0].set_ylim(0, 1)
        self.axes[0].tick_params(  # type: ignore[attr-defined]
            axis='both', labelbottom=False, left=False, labelleft=False
        )

        self.axes.append(
            self.fig.add_subplot(2, 1, 2, sharex=self.axes[0], sharey=self.axes[0])
        )
        self.axes[1].grid(ls='--')  # type: ignore[call-arg]
        self.axes[1].tick_params(  # type: ignore[attr-defined]
            axis='both', left=False, labelleft=False
        )
        self.axes[1].set_xlabel(r'Seconds since t$_0$')

    def _add_entries_to_plot(self, ax: plt.Axes, entries: dict[str, Any]) -> None:
        """Adds entries to a plot.

        Parameters:
            ax: instance of matplotlib Axes
            entries: dict as returned by self._get_labels() or self._get_files()
        """
        i = 0
        for key, item in entries.items():
            y_loc = i / len(entries.keys()) * 0.9 + 0.05
            if item['found']:
                ax.axvline(
                    item['latency'], ls='-', color=self.cmap(y_loc)
                )  # type: ignore[call-arg]
                ax.plot(
                    [item['latency'], item['latency'] + 15],
                    [y_loc, y_loc],
                    color=self.cmap(y_loc),
                )
                ax.text(  # type: ignore[attr-defined]
                    item['latency'] + 17,
                    y_loc,
                    key,
                    color=self.cmap(y_loc),
                    va='center',
                )
            i += 1

    def _save_analize_sev_history(self, outdir: Path) -> None:
        """Saves the dump of AnalizeLogsSuperEvents and AnalizePipelinesSEvents.

        Parameters:
            outdir: Output directory.
        """
        filename = outdir / ('%s_analize_sev_history.txt' % str(self.sevent_id))

        dump_log_lines = []

        # -------------------------------
        # Ouput data event
        # -------------------------------
        # -------------------------------
        # Ouput log LABELS
        # -------------------------------
        dump_log_lines.append(
            '  ================== S-event        ============================'
        )

        dump_log_lines.append(
            '   superevent_id: {}'.format(self.sev_values['superevent_id'])
        )
        dump_log_lines.append('      preferd_id: {}'.format(self.gev_values['graceid']))
        dump_log_lines.append('           group: {}'.format(self.gev_values['group']))
        dump_log_lines.append(
            '        pipeline: {}'.format(self.gev_values['pipeline'])
        )
        dump_log_lines.append(f'  is_significant: {self.is_significant}')
        dump_log_lines.append(f'  should_publish: {self.should_publish}')

        # -------------------------------
        # Ouput log upload events
        # -------------------------------
        for history_index in ['added', 'prefered']:
            data_upload_events = self.history_properties[history_index]
            dump_log_lines.append(
                f'  ===== {history_index:8} EVENT HISTORY ================='
            )
            for data_upload_event in data_upload_events:
                id_event = data_upload_event[1]
                try:
                    data_event = self.sevent_data['gevents'][id_event]
                except KeyError:
                    data_event = {
                        'group': '--',
                        'pipeline': '--',
                        'search': '--',
                        'far': 0.0,
                    }
                    credible90 = 0.0
                try:
                    if data_event['group'].lower() == 'cbc':
                        localization = 'bayestar.multiorder.fits'
                    elif data_event['group'].lower() == 'burst':
                        localization = (
                            data_event['pipeline'].lower() + '.multiorder.fits'
                        )
                    else:
                        localization = 'dummy'
                    filepath = self.path / id_event / localization
                    self._get_file_dataproduct_ev(localization, id_event, filepath)
                    moc90 = mocpy.MOC.from_multiordermap_fits_file(
                        filepath, cumul_to=0.9
                    )
                    credible90 = moc90.sky_fraction
                    skymap_fits = astropy.io.fits.open(filepath)
                    LOGBCI = skymap_fits[1].header['LOGBCI']
                except KeyError:
                    LOGBCI = 0
                except ValueError:
                    LOGBCI = 0
                    credible90 = 0.0
                try:
                    snr_event = data_event['extra_attributes']['CoincInspiral']['snr']
                except KeyError:
                    snr_event = 0.0
                dump_log_lines.append(
                    '  {:8.1f}s {:10} FAR={:8.3g} SNR={:5.2f}'
                    ' sky90%= {:8.3f} deg2 LOGBCI={:5.2f} {}'.format(
                        data_upload_event[0],
                        id_event,
                        data_event['far'],
                        snr_event,
                        credible90 * (360**2) / np.pi,
                        LOGBCI,
                        str((data_event['pipeline'], data_event['search'])),
                    )
                )
        # -------------------------------
        # Ouput log LABELS and tags
        # -------------------------------

        dump_log_lines.append(
            '  ==================  HISTORY ============================='
        )
        for kind in ['lables', 'rlables', 'gcn_received']:
            dump_log_lines.append(f'  ******** Property: {kind:15}  *******')
            data_lables = self.history_properties[kind]
            for data_lable in data_lables:
                dump_log_lines.append('  {:8.1f}s {:30} - log({})'.format(*data_lable))

        # -------------------------------
        # Ouput log G-events and groups
        # -------------------------------
        dump_log_lines.append(
            '  ==================     EVENTS TYPE   ============================'
        )
        for group_event in self.group_events:
            dump_log_lines.append(
                '  -- {:25} FAR={:8.3} : {}'.format(
                    str((group_event[0], group_event[1])),
                    np.min(self.group_fars[group_event]),
                    self.group_events[group_event],
                )
            )

        # -------------------------------
        # Ouput alert History
        # -------------------------------
        dump_log_lines.append(
            '  ==================    ALERT HISTORY    ============================'
        )
        for alert_kind in self.history_alerts:
            dump_log_lines.append(f'  KIND {alert_kind}')
            for alert in self.history_alerts[alert_kind]:
                dump_log_lines.append(
                    '{:10.1f}s {:15} {:36} - log({})'.format(
                        alert[0], alert[1], alert[2] + ',' + str(alert[3]), alert[4]
                    )
                )

        # -------------------------------
        # Ouput Data Product  History
        # -------------------------------
        dump_log_lines.append(
            '  ==================    DATA PRODUCTS HISTORY     ==================='
        )
        for alert_kind in self.history_dataproducts:
            dump_log_lines.append(f'  KIND {alert_kind}')
            for dataproduct in self.history_dataproducts[alert_kind]:
                dump_log_lines.append(
                    '{:10.1f}s file= {:30} ...{} - log({})'.format(
                        dataproduct[0],
                        dataproduct[1] + ',' + str(dataproduct[2]),
                        dataproduct[3][-12:],
                        dataproduct[4],
                    )
                )

        # -------------------------------
        # Ouput Data Product
        # -------------------------------
        dump_log_lines.append(
            '  ==================    DATA PRODUCTS  =============================='
        )
        dump_log_lines.append(f'  {list(self.dataproducts)}')
        for dataproduct in ['p_astro', 'em_bright', 'gwskynet']:
            dump_log_lines.append(f'  [{dataproduct}]')
            dataproducts = self.dataproducts[dataproduct]
            for data_filename in dataproducts:
                data_json = json.loads(dataproducts[data_filename])
                prop_keys = list(data_json)
                prop_keys.sort()
                data_json = ','.join(
                    [f'{prop}={data_json[prop]:9.4g} ' for prop in prop_keys]
                )
                dump_log_lines.append(f'  -- {data_filename:35} {data_json}')
        for dataproduct in ['multiorder']:
            dump_log_lines.append(f'  [{dataproduct}]')
            dataproducts = self.dataproducts[dataproduct]
            for data_filename in dataproducts:
                fitscontent = dataproducts[data_filename]
                moc90 = mocpy.MOC.from_multiordermap_fits_file(
                    self.path / data_filename, cumul_to=0.9
                )
                try:
                    skymap_fits = astropy.io.fits.open(io.BytesIO(fitscontent))
                    LOGBCI = skymap_fits[1].header['LOGBCI']
                except KeyError:
                    LOGBCI = 0
                dump_log_lines.append(
                    '  -- {:35} size={} sky90%={:7.5f} LOGBCI={:5.2f}'.format(
                        data_filename,
                        len(fitscontent),
                        moc90.sky_fraction,
                        LOGBCI,
                    )
                )

        dump_log_lines.append(
            '  ==================================================================='
        )
        if self.loginfo:
            for line in dump_log_lines:
                logger.info(line)

        with open(filename, 'w') as stream:
            stream.writelines(line + '\n' for line in dump_log_lines)
        logger.info(f'History saved to {str(filename)}')
