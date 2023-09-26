import pytest  # noqa
from pyhomogenize import open_xrdataset

import index_calculator as xcalc

from conftest import (
    pr_day_netcdf,
    snw_day_netcdf,
    tas_1hr_netcdf,
    tas_day_netcdf,
    tas_eobs_day_netcdf,
    uas_day_netcdf,
    vas_day_netcdf,
)

    
def test_snw_index_calculator():
    data = snw_day_netcdf()
    snw_ds = open_xrdataset(data)
    idx = xcalc.index_calculator(
        ds=snw_ds,
        freq="week",
        index="SCD",
        crop_time_axis=False,
        project="CORDEX",
        institution="test institution",
        institution_id="TEST",
        contact="test@test.de",
        write=True,
    )
    return idx

def test_snw_const_index_calculator():
    data = snw_day_netcdf()
    snw_ds = open_xrdataset(data)
    xcalc.index_calculator(
        ds=snw_ds,
        freq="week",
        index="SCD",
        crop_time_axis=False,
        project="CORDEX",
        institution="test institution",
        institution_id="TEST",
        contact="test@test.de",
        write=True,
        const="300 kg m-3",
    )

def test_uas_vas_index_calculator():
    data_uas = uas_day_netcdf()
    data_vas = vas_day_netcdf()
    sfcWind_ds = open_xrdataset([data_uas, data_vas])
    xcalc.index_calculator(
        ds=sfcWind_ds,
        freq="week",
        index="FG",
        crop_time_axis=False,
        project="CORDEX",
        institution="test institution",
        institution_id="TEST",
        contact="test@test.de",
        write=True,
    )
    
def test_1hr_index_calculator():
    data = tas_1hr_netcdf()
    tas_ds = open_xrdataset(data)
    xcalc.index_calculator(
        ds=tas_ds,
        freq="week",
        index="TG",
        crop_time_axis=False,
        project="CORDEX",
        institution="test institution",
        institution_id="TEST",
        contact="test@test.de",
        write=True,
    )

def test_eobs_index_calculator():
    data = tas_eobs_day_netcdf()
    tas_ds = open_xrdataset(data)
    xcalc.index_calculator(
        ds=tas_ds,
        freq="week",
        index="TG",
        crop_time_axis=False,
        project="EOBS",
        institution="test institution",
        institution_id="TEST",
        contact="test@test.de",
        write=True,
    )
    
test_eobs_index_calculator()
