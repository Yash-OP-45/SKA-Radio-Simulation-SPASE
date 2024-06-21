import csv
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.time import Time
import astropy.units as u

#conversion function
def altaz_to_radec(in_csv, out_csv):
    #Observatory Point (remains the same: F-110, Hall5, IITK)

    latitude = 26.509951955711866 * u.deg
    longitude = 80.22809216211232 * u.deg
    elevation = 123.51 * u.m
    curr_location = EarthLocation(lat=latitude, lon=longitude, height=elevation)
    
    ra_dec_dict = []  
    with open(in_csv, 'r') as input_file:
        reader = csv.DictReader(input_file)
        for column in reader:
            alt = float(column['alt'])
            az = float(column['az'])
            time = Time(column['time'])
            
            alt_az = AltAz(location=curr_location, obstime=time)
            sky_coord_obj = SkyCoord(alt=alt * u.deg, az=az * u.deg, frame=alt_az)
            radec = sky_coord_obj.transform_to('icrs')
            
            ra = radec.ra.deg
            dec = radec.dec.deg
            
            ra_dec_dict.append({'ra_deg': ra, 'dec_deg': dec})
    
    with open(out_csv, 'w', newline='') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=['ra_deg', 'dec_deg','I','Q','U','V','ref_freq_hz','spectral_index','rotation_measure','major_axis_arcsec','minor_axis_arcsec','position_angle_deg'])
        #General format of OSKAR SkyModel 
        writer.writeheader()
        writer.writerows(ra_dec_dict)


in_csv = r'D:\Project - Simulation of the nightsky\First Simulation\SKY Model\OSKAR Skymodel format\ALTAZ.csv'
out_csv = r'D:\Project - Simulation of the nightsky\First Simulation\SKY Model\OSKAR Skymodel format\altaz to radec to OSKAR SkyModel format.csv'
altaz_to_radec(in_csv, out_csv)