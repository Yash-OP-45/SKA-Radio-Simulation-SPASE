#!/usr/bin/env python3

"""Script to run LOW station beam error simulations at spot frequencies."""

from __future__ import print_function, division
import concurrent.futures
import json
import logging
import os
import sys

from astropy.io import fits
from astropy.time import Time, TimeDelta
import matplotlib
matplotlib.use('Agg')
# pylint: disable=wrong-import-position
import matplotlib.pyplot as plt
import numpy
import oskar


LOG = logging.getLogger()


def bright_sources():
    """Returns a list of bright A-team sources."""
    # Sgr A: guesstimates only!
    # For A: data from the Molonglo Southern 4 Jy sample (VizieR).
    # Others from GLEAM reference paper, Hurley-Walker et al. (2017), Table 2.
    return numpy.array((
        [266.41683, -29.00781,  2000,0,0,0,   0,    0,    0, 3600, 3600, 0],
        [ 50.67375, -37.20833,   528,0,0,0, 178e6, -0.51, 0, 0, 0, 0],  # For
        [201.36667, -43.01917,  1370,0,0,0, 200e6, -0.50, 0, 0, 0, 0],  # Cen
        [139.52500, -12.09556,   280,0,0,0, 200e6, -0.96, 0, 0, 0, 0],  # Hyd
        [ 79.95833, -45.77889,   390,0,0,0, 200e6, -0.99, 0, 0, 0, 0],  # Pic
        [252.78333,   4.99250,   377,0,0,0, 200e6, -1.07, 0, 0, 0, 0],  # Her
        [187.70417,  12.39111,   861,0,0,0, 200e6, -0.86, 0, 0, 0, 0],  # Vir
        [ 83.63333,  22.01444,  1340,0,0,0, 200e6, -0.22, 0, 0, 0, 0],  # Tau
        [299.86667,  40.73389,  7920,0,0,0, 200e6, -0.78, 0, 0, 0, 0],  # Cyg
        [350.86667,  58.81167, 11900,0,0,0, 200e6, -0.41, 0, 0, 0, 0]   # Cas
        ))


def get_start_time(ra0_deg, length_sec):
    """Returns optimal start time for field RA and observation length."""
    t = Time('2000-01-01 00:00:00', scale='utc', location=('116.764d', '0d'))
    dt_hours = 24.0 - t.sidereal_time('apparent').hour + (ra0_deg / 15.0)
    start = t + TimeDelta(dt_hours * 3600.0 - length_sec / 2.0, format='sec')
    return start.value


def make_vis_data(settings, sky, tel):
    """Run simulation using supplied settings."""
    if os.path.exists(settings['interferometer/oskar_vis_filename']):
        LOG.info("Skipping simulation, as output data already exist.")
        return
    LOG.info("Simulating %s", settings['interferometer/oskar_vis_filename'])
    sim = oskar.Interferometer(settings=settings)
    sim.set_sky_model(sky)
    sim.set_telescope_model(tel)
    sim.run()


def make_sky_model(sky0, settings, radius_deg, flux_min_outer_jy):
    """Filter sky model.

    Includes all sources within the given radius, and sources above the
    specified flux outside this radius.
    """
    # Get pointing centre.
    ra0_deg = float(settings['observation/phase_centre_ra_deg'])
    dec0_deg = float(settings['observation/phase_centre_dec_deg'])

    # Create "inner" and "outer" sky models.
    sky_inner = sky0.create_copy()
    sky_outer = sky0.create_copy()
    sky_inner.filter_by_radius(0.0, radius_deg, ra0_deg, dec0_deg)
    sky_outer.filter_by_radius(radius_deg, 180.0, ra0_deg, dec0_deg)
    sky_outer.filter_by_flux(flux_min_outer_jy, 1e9)
    LOG.info("Number of sources in sky0: %d", sky0.num_sources)
    LOG.info("Number of sources in inner sky model: %d", sky_inner.num_sources)
    LOG.info("Number of sources in outer sky model above %.3f Jy: %d",
             flux_min_outer_jy, sky_outer.num_sources)
    sky_outer.append(sky_inner)
    LOG.info("Number of sources in output sky model: %d", sky_outer.num_sources)
    return sky_outer


def make_diff_image_stats(filename1, filename2, use_w_projection,
                          out_image_root=None):
    """Make an image of the difference between two visibility data sets.

    This function assumes that the observation parameters for both data sets
    are identical. (It will fail horribly otherwise!)
    """
    # Set up an imager.
    (hdr1, handle1) = oskar.VisHeader.read(filename1)
    (hdr2, handle2) = oskar.VisHeader.read(filename2)
    frequency_hz = hdr1.freq_start_hz
    fov_ref_frequency_hz = 140e6
    fov_ref_deg = 5.0
    fov_deg = fov_ref_deg * (fov_ref_frequency_hz / frequency_hz)
    imager = oskar.Imager(precision='double')
    imager.set(fov_deg=fov_deg, image_size=8192,
               fft_on_gpu=True, grid_on_gpu=True)
    if out_image_root is not None:
        imager.output_root = out_image_root

    LOG.info("Imaging differences between '%s' and '%s'", filename1, filename2)
    block1 = oskar.VisBlock.create_from_header(hdr1)
    block2 = oskar.VisBlock.create_from_header(hdr2)
    if hdr1.num_blocks != hdr2.num_blocks:
        raise RuntimeError("'%s' and '%s' have different dimensions!" %
                           (filename1, filename2))
    if use_w_projection:
        imager.set(algorithm='W-projection')
        imager.coords_only = True
        for i_block in range(hdr1.num_blocks):
            block1.read(hdr1, handle1, i_block)
            imager.update_from_block(hdr1, block1)
        imager.coords_only = False
        imager.check_init()
        LOG.info("Using %d W-planes", imager.num_w_planes)
    executor = concurrent.futures.ThreadPoolExecutor(2)
    for i_block in range(hdr1.num_blocks):
        tasks_read = []
        tasks_read.append(executor.submit(block1.read, hdr1, handle1, i_block))
        tasks_read.append(executor.submit(block2.read, hdr2, handle2, i_block))
        concurrent.futures.wait(tasks_read)
        block1.cross_correlations()[...] -= block2.cross_correlations()
        imager.update_from_block(hdr1, block1)
    del handle1, handle2, hdr1, hdr2, block1, block2

    # Finalise image and return it to Python.
    output = imager.finalise(return_images=1)
    image = output['images'][0]

    LOG.info("Generating image statistics")
    image_size = imager.image_size
    box_size = int(0.1 * image_size)
    centre = image[
        (image_size - box_size)//2:(image_size + box_size)//2,
        (image_size - box_size)//2:(image_size + box_size)//2]
    del imager
    return {
        'image_medianabs': numpy.median(numpy.abs(image)),
        'image_mean': numpy.mean(image),
        'image_std': numpy.std(image),
        'image_rms': numpy.sqrt(numpy.mean(image**2)),
        'image_centre_mean': numpy.mean(centre),
        'image_centre_std': numpy.std(centre),
        'image_centre_rms': numpy.sqrt(numpy.mean(centre**2))
    }


def make_plot(prefix, field_name, metric_key, results,
              axis_freq, axis_gain):
    """Plot selected results."""
    # Get data for contour plot.
    X, Y = numpy.meshgrid(axis_freq, axis_gain)
    Z = numpy.zeros(X.shape)
    for freq, gain, z in numpy.nditer([X, Y, Z], op_flags=['readwrite']):
        key = '%s_%s_%d_MHz_%.3f_dB' % (prefix, field_name, freq, gain)
        if key in results:
            z[...] = numpy.log10(results[key][metric_key])
    ax1 = plt.subplot(111)
    ax1.set_yscale('log')

    # Scatter plot.
    sp = ax1.scatter(X, Y, c=Z, cmap='plasma')

    # Contour plot.
    cp = ax1.contour(X, Y, Z, cmap='plasma')
    levels = cp.levels
    print(prefix, field_name, len(levels))
    if len(levels) > 9:
        levels = levels[::2]
    clabels = plt.clabel(cp, levels, inline=False, fontsize=10, fmt='%1.1f')
    for txt in clabels:
        txt.set_bbox(dict(facecolor='white', edgecolor='none', pad=1))

    # Title and axis labels.
    metric_name = '[ UNKNOWN ]'
    if metric_key == 'image_centre_rms':
        metric_name = 'Central RMS [Jy/beam]'
    elif metric_key == 'image_medianabs':
        metric_name = 'MEDIAN(ABS(image)) [Jy/beam]'
    sky_model = 'GLEAM'
    if 'A-team' in prefix:
        sky_model = sky_model + ' + A-team'
    plt.title('%s for %s field (%s)' % (metric_name, field_name, sky_model))
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('Element gain standard deviation [dB]')
    cbar = plt.colorbar(sp)
    cbar.set_label('log10(%s)' % metric_name)
    plt.savefig('%s_%s_%s.png' % (prefix, field_name, metric_key))
    plt.close('all')


def run_single(prefix_field, settings, sky, tel,
               freq_MHz, gain_std_dB, out0_name, results):
    """Run a single simulation and generate image statistics for it."""
    out = '%s_%d_MHz_%.3f_dB' % (prefix_field, freq_MHz, gain_std_dB)
    if out in results:
        LOG.info("Using cached results for '%s'", out)
        return
    out_name = out + '.vis'
    gain_std = numpy.power(10.0, gain_std_dB / 20.0) - 1.0
    tel.override_element_gains(1.0, gain_std)
    tel.override_element_cable_length_errors(0.015)
    settings['interferometer/oskar_vis_filename'] = out_name
    make_vis_data(settings, sky, tel)
    out_image_root = out
    use_w_projection = True
    if str(settings['interferometer/ignore_w_components']).lower() == 'true':
        use_w_projection = False
    results[out] = make_diff_image_stats(out0_name, out_name, use_w_projection,
                                         out_image_root)


def run_set(prefix, base_settings, fields, axis_freq, axis_gain, plot_only):
    """Runs a set of simulations."""
    if not plot_only:
        # Load base telescope model.
        settings = oskar.SettingsTree(r'D:\Project-Simulation of the nightsky\First Simulation\OSKAR-2.7-Example-Data\oskar_sim_interferometer.ini')
        settings.from_dict(base_settings)
        tel = oskar.Telescope(settings=settings)

        # Load base sky model
        sky0 = oskar.Sky()
        if 'GLEAM' in prefix:
            # Load GLEAM catalogue from FITS binary table.
            hdulist = fits.open('GLEAM_EGC.fits')
            # pylint: disable=no-member
            cols = hdulist[1].data[0].array
            data = numpy.column_stack(
                (cols['RAJ2000'], cols['DEJ2000'], cols['peak_flux_wide']))
            data = data[data[:, 2].argsort()[::-1]]
            sky_gleam = oskar.Sky.from_array(data)
            sky0.append(sky_gleam)
        if 'A-team' in prefix:
            sky_bright = oskar.Sky.from_array(bright_sources())
            sky0.append(sky_bright)

    # Iterate over fields.
    for field_name, field in fields.items():
        # Load result set, if it exists.
        prefix_field = prefix + '_' + field_name
        results = {}
        json_file = prefix_field + '_results.json'
        if os.path.exists(json_file):
            with open(json_file, 'r') as input_file:
                results = json.load(input_file)

        # Iterate over frequencies.
        if not plot_only:
            for freq_MHz in axis_freq:
                # Update settings for field.
                settings_dict = base_settings.copy()
                settings_dict.update(field)
                settings.from_dict(settings_dict)
                ra_deg = float(settings['observation/phase_centre_ra_deg'])
                dec_deg = float(settings['observation/phase_centre_dec_deg'])
                length_sec = float(settings['observation/length'])
                settings['observation/start_frequency_hz'] = str(freq_MHz * 1e6)
                settings['observation/start_time_utc'] = get_start_time(
                    ra_deg, length_sec)
                tel.set_phase_centre(ra_deg, dec_deg)

                # Create the sky model.
                sky = make_sky_model(sky0, settings, 20.0, 10.0)
                settings['interferometer/ignore_w_components'] = 'true'
                if 'A-team' in prefix:
                    settings['interferometer/ignore_w_components'] = 'false'

                # Simulate the 'perfect' case.
                tel.override_element_gains(1.0, 0.0)
                tel.override_element_cable_length_errors(0.0)
                out0_name = '%s_%d_MHz_no_errors.vis' % (prefix_field, freq_MHz)
                settings['interferometer/oskar_vis_filename'] = out0_name
                make_vis_data(settings, sky, tel)

                # Simulate the error cases.
                for gain_std_dB in axis_gain:
                    run_single(prefix_field, settings, sky, tel,
                               freq_MHz, gain_std_dB, out0_name, results)

        # Generate plot for the field.
        make_plot(prefix, field_name, 'image_centre_rms',
                  results, axis_freq, axis_gain)
        make_plot(prefix, field_name, 'image_medianabs',
                  results, axis_freq, axis_gain)

        # Save result set.
        with open(json_file, 'w') as output_file:
            json.dump(results, output_file, indent=4)


def main():
    """Main function."""
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    LOG.addHandler(handler)
    LOG.setLevel(logging.INFO)

    # Define common settings.
    base_settings = {
        'simulator': {
            'double_precision': 'true',
            'use_gpus': 'true',
            'max_sources_per_chunk': '23000'
        },
        'observation' : {
            'frequency_inc_hz': '100e3',
            'length': '14400.0',
            'num_time_steps': '240'
        },
        'telescope': {
            'input_directory': 'SKA1-LOW_SKO-0000422_Rev3_38m_SKALA4_spot_frequencies.tm'
        },
        'interferometer': {
            'channel_bandwidth_hz': '100e3',
            'time_average_sec': '1.0',
            'max_time_samples_per_block': '4'
        }
    }

    # Define axes of parameter space.
    fields = {
        'EoR0': {
            'observation/phase_centre_ra_deg': '0.0',
            'observation/phase_centre_dec_deg': '-27.0'
        },
        'EoR1': {
            'observation/phase_centre_ra_deg': '60.0',
            'observation/phase_centre_dec_deg': '-30.0'
        },
        'EoR2': {
            'observation/phase_centre_ra_deg': '170.0',
            'observation/phase_centre_dec_deg': '-10.0'
        }
    }
    axis_freq = [50, 70, 110, 137, 160, 230, 320]
    axis_gain = [0.005, 0.01, 0.02, 0.04, 0.08, 0.16, 0.32, 0.64]

    # GLEAM + A-team sky model simulations.
    plot_only = False
    run_set('GLEAM_A-team', base_settings,
            fields, axis_freq, axis_gain, plot_only)


if __name__ == '__main__':
    main()