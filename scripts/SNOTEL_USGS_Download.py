# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 09:39:53 2024

@author: A01797988
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 18:07:26 2023

@author: Hyrum
"""

# import libraries
import pandas as pd
import numpy as np
import datetime
import os
import dataretrieval.nwis as nwis
import zeep
import pickle

directory = r'INSERT DIRECTORY WHERE FILES SHOULD BE SAVED HERE!'

# =============================================================================
# DATA RETRIEVAL FUNCTIONS
# =============================================================================
#NRCS WCC database acess
url = 'https://wcc.sc.egov.usda.gov/awdbWebService/services?WSDL'
client = zeep.Client(url)

# get snotel station codes and locations
def get_snotel_stations(states, network):
    result = client.service.getStations(stateCds=states, networkCds=network, logicalAnd=True)
    result = zeep.helpers.serialize_object(result)
    station_list = pd.DataFrame.from_dict(result)
    return station_list


# function for converting daily WCC data into correct format
def wcc_format(result):
    result = zeep.helpers.serialize_object(result)
    result = result[0]
    val = result['values']
    if len(val) >0:
        st = result['beginDate']
        et = result['endDate']
        df = pd.DataFrame()
        df['DataValue'] = pd.DataFrame.from_dict(val)
        flags = pd.DataFrame().from_dict(result['flags'])
        df['flags'] = flags
        dt = pd.date_range(pd.to_datetime(st), pd.to_datetime(et), freq='D')
        if len(dt) == len(df):
            df['LocalDateTime'] = dt
            df['DataValue'] = pd.to_numeric(df['DataValue'])
            df = df.sort_values(by=['LocalDateTime'])
            df['LocalDateTime'] = pd.to_datetime(df['LocalDateTime'])
            df = df.set_index('LocalDateTime', drop=True)
            df.drop('flags', axis=1)
    return df

# function for getting SNOTEL station meta data
def snotel_meta(stationTriplet):
    meta = client.service.getStationMetadata(stationTriplet=stationTriplet)
    meta = zeep.helpers.serialize_object(meta)
    meta = pd.DataFrame.from_dict(meta, orient='index')
    meta = meta.T
    return meta

# function for getting SNOTEL data
def snotel_data(stationTriplet):
    data = {}
    meta = snotel_meta(stationTriplet)
    begin = meta['beginDate'].values[0]
    begin = str(pd.to_datetime(begin).date())
    end = datetime.date.today()
    
    prcpsa = client.service.getData(stationTriplets=stationTriplet, elementCd='PRCPSA', ordinal=1, duration='DAILY', getFlags='true', beginDate=begin, endDate=end, alwaysReturnDailyFeb29='false')
    prcpsa = wcc_format(prcpsa)
    
    swe = client.service.getData(stationTriplets=stationTriplet, elementCd='WTEQ', ordinal=1, duration='DAILY', getFlags='true', beginDate=begin, endDate=end, alwaysReturnDailyFeb29='false')
    swe = wcc_format(swe)
    
    ## sm is soil moisture, st is soil temperature. The numbers denote depths in centimeters. There is no standard depth at which soil moisture and temperature is taken. It varies between stations.
    
    # smv2 = client.service.getData(stationTriplets=stationTriplet, elementCd='SMV', ordinal=1, duration='DAILY', heightDepth={'unitCd':'in', 'value':-2}, getFlags='true', beginDate=begin, endDate=end, alwaysReturnDailyFeb29='false')
    # try:
    #     smv2 = wcc_format(smv2)
    #     data['smv2'] = smv2
    # except:
    #     pass
    
    # stv2 = client.service.getData(stationTriplets=stationTriplet, elementCd='STV', ordinal=1, duration='DAILY', heightDepth={'unitCd':'in', 'value':-2}, getFlags='true', beginDate=begin, endDate=end, alwaysReturnDailyFeb29='false')
    # try:
    #     stv2 = wcc_format(stv2)
    #     data['stv2'] = stv2
    # except:
    #     pass
    
    # smv4 = client.service.getData(stationTriplets=stationTriplet, elementCd='SMV', ordinal=1, duration='DAILY', heightDepth={'unitCd':'in', 'value':-4}, getFlags='true', beginDate=begin, endDate=end, alwaysReturnDailyFeb29='false')
    # try:
    #     smv4 = wcc_format(smv4)
    #     data['smv4'] = smv4
    # except:
    #     pass
    
    # stv4 = client.service.getData(stationTriplets=stationTriplet, elementCd='STV', ordinal=1, duration='DAILY', heightDepth={'unitCd':'in', 'value':-4}, getFlags='true', beginDate=begin, endDate=end, alwaysReturnDailyFeb29='false')
    # try:
    #     smv4 = wcc_format(smv4)
    #     data['smv4'] = smv4
    # except:
    #     pass
    
    # smv8 = client.service.getData(stationTriplets=stationTriplet, elementCd='SMV', ordinal=1, duration='DAILY', heightDepth={'unitCd':'in', 'value':-8}, getFlags='true', beginDate=begin, endDate=end, alwaysReturnDailyFeb29='false')
    # try:
    #     smv4 = wcc_format(smv4)
    #     data['smv4'] = smv4
    # except:
    #     pass
    
    # stv8 = client.service.getData(stationTriplets=stationTriplet, elementCd='STV', ordinal=1, duration='DAILY', heightDepth={'unitCd':'in', 'value':-8}, getFlags='true', beginDate=begin, endDate=end, alwaysReturnDailyFeb29='false')
    # try:
    #     stv8 = wcc_format(stv8)
    #     data['stv8'] = stv8
    # except:
    #     pass
    
    # smv20 = client.service.getData(stationTriplets=stationTriplet, elementCd='SMV', ordinal=1, duration='DAILY', heightDepth={'unitCd':'in', 'value':-20}, getFlags='true', beginDate=begin, endDate=end, alwaysReturnDailyFeb29='false')
    # try:
    #     smv20 = wcc_format(smv20)
    #     data['smv20'] = smv20
    # except:
    #     pass
    
    # stv20 = client.service.getData(stationTriplets=stationTriplet, elementCd='STV', ordinal=1, duration='DAILY', heightDepth={'unitCd':'in', 'value':-20}, getFlags='true', beginDate=begin, endDate=end, alwaysReturnDailyFeb29='false')
    # try:
    #     stv20 = wcc_format(stv20)
    #     data['stv20'] = stv20
    # except:
    #     pass
    
    # smv40 = client.service.getData(stationTriplets=stationTriplet, elementCd='SMV', ordinal=1, duration='DAILY', heightDepth={'unitCd':'in', 'value':-40}, getFlags='true', beginDate=begin, endDate=end, alwaysReturnDailyFeb29='false')
    # try:
    #     smv40 = wcc_format(smv40)
    #     data['smv40'] = smv40
    # except:
    #     pass
    
    # stv40 = client.service.getData(stationTriplets=stationTriplet, elementCd='STV', ordinal=1, duration='DAILY', heightDepth={'unitCd':'in', 'value':-40}, getFlags='true', beginDate=begin, endDate=end, alwaysReturnDailyFeb29='false')
    # try:
    #     stv40 = wcc_format(stv40)
    #     data['stv40'] = stv40
    # except:
    #     pass
    
    tavg = client.service.getData(stationTriplets=stationTriplet, elementCd='TAVG', ordinal=1, duration='DAILY', getFlags='true', beginDate=begin, endDate=end, alwaysReturnDailyFeb29='false')
    try:
        tavg = wcc_format(tavg)
        data['tavg'] = tavg
    except:
        pass
    
    snow = swe.copy(deep=True)
    snow['DataValue'] = -1.0*snow['DataValue'].diff(periods=-1)+0
    snow.loc[snow['DataValue'] < 0, 'DataValue'] = 0
    
    rain = prcpsa.copy(deep=True)
    rain['DataValue'] = rain['DataValue'].sub(snow['DataValue'], fill_value=None)
    
    data['prcpsa'] = prcpsa
    data['swe'] = swe
    data['snow'] = snow
    data['rain'] = rain
    
    return data
    
# function for getting daily USGS discharge data
def usgs_data(stationID):
    df = nwis.get_record(sites=str(stationID), service='dv', start='1900-10-01', parameterCd='00060')
    if len(df) == 0:
        df = usgs_iv_data(stationID)
        return df
    if '00060_Mean' not in df.columns:
        df = pd.DataFrame()
        return df
    df = df.reset_index()
    df = df.rename(columns={'00060_Mean':'DataValue', 'datetime':'LocalDateTime'})
    df = df.drop(columns=['00060_Mean_cd', 'site_no'])
    df['LocalDateTime'] = pd.to_datetime(df['LocalDateTime'])
    df['LocalDateTime'] = df['LocalDateTime'].dt.tz_localize(None)
    df = df.set_index('LocalDateTime', drop=False)
    df['DataValue'] = df['DataValue'].replace(-999999, np.nan)
    df = df[['DataValue']]
    return df

# get USGS gage station codes and locations
def get_usgs_meta(state):
    df = nwis.get_record(stateCd=state, parameterCd='00060', siteType='ST', siteStatus='active', service='site')
    df = df.rename(columns={'agency_cd' : 'Agency'
                            , 'site_no' : 'Site identification number'
                            , 'station_nm' : 'Site name'
                            , 'site_tp_cd' : 'Site type'
                            , 'lat_va' : 'DMS latitude'
                            , 'long_va' : 'DMS longitude'
                            , 'dec_lat_va' : 'latitude'
                            , 'dec_long_va' : 'longitude'
                            , 'coord_meth_cd' : 'Latitude-longitude method'
                            , 'coord_acy_cd' : 'Latitude-longitude accuracy'
                            , 'coord_datum_cd' : 'Latitude-longitude datum'
                            , 'dec_coord_datum_cd' : 'Decimal Latitude-longitude datum'
                            , 'district_cd' : 'District code'
                            , 'state_cd' : 'State code'
                            , 'county_cd' : 'County code'
                            , 'country_cd' : 'Country code'
                            , 'land_net_ds' : 'Land net location description'
                            , 'map_nm' : 'Name of location map'
                            , 'map_scale_fc' : 'Scale of location map'
                            , 'alt_va' : 'Altitude of Gage/land surface'
                            , 'alt_meth_cd' : 'Method altitude determined'
                            , 'alt_acy_va' : 'Altitude accuracy'
                            , 'alt_datum_cd' : 'Altitude datum'
                            , 'huc_cd' : 'Hydrologic unit code'
                            , 'basin_cd' : 'Drainage basin code'
                            , 'topo_cd' : 'Topographic setting code'
                            , 'instruments_cd' : 'Flags for instruments at site'
                            , 'construction_dt' : 'Date of first construction'
                            , 'inventory_dt' : 'Date site established or inventoried'
                            , 'drain_area_va' : 'Drainage area'
                            , 'contrib_drain_area_va' : 'Contributing drainage area'
                            , 'tz_cd' : 'Time Zone abbreviation'
                            , 'local_time_fg' : 'Site honors Daylight Savings Time'
                            , 'reliability_cd' : 'Data reliability code'
                            , 'gw_file_cd' : 'Data-other GW files'
                            , 'nat_aqfr_cd' : 'National aquifer code'
                            , 'aqfr_cd' : 'Local aquifer code'
                            , 'aqfr_type_cd' : 'Local aquifer type code'
                            , 'well_depth_va' : 'Well depth'
                            , 'hole_depth_va' : 'Hole depth'
                            , 'depth_src_cd' : 'Source of depth data'
                            , 'project_no' : 'Project number'})
    return df

def gage_meta(stationID):
    df = nwis.get_record(sites=str(stationID), parameterCd='00060', siteType='ST', siteStatus='active', service='site')
    df = df.rename(columns={'agency_cd' : 'Agency'
                            , 'site_no' : 'Site identification number'
                            , 'station_nm' : 'Site name'
                            , 'site_tp_cd' : 'Site type'
                            , 'lat_va' : 'DMS latitude'
                            , 'long_va' : 'DMS longitude'
                            , 'dec_lat_va' : 'latitude'
                            , 'dec_long_va' : 'longitude'
                            , 'coord_meth_cd' : 'Latitude-longitude method'
                            , 'coord_acy_cd' : 'Latitude-longitude accuracy'
                            , 'coord_datum_cd' : 'Latitude-longitude datum'
                            , 'dec_coord_datum_cd' : 'Decimal Latitude-longitude datum'
                            , 'district_cd' : 'District code'
                            , 'state_cd' : 'State code'
                            , 'county_cd' : 'County code'
                            , 'country_cd' : 'Country code'
                            , 'land_net_ds' : 'Land net location description'
                            , 'map_nm' : 'Name of location map'
                            , 'map_scale_fc' : 'Scale of location map'
                            , 'alt_va' : 'Altitude of Gage/land surface'
                            , 'alt_meth_cd' : 'Method altitude determined'
                            , 'alt_acy_va' : 'Altitude accuracy'
                            , 'alt_datum_cd' : 'Altitude datum'
                            , 'huc_cd' : 'Hydrologic unit code'
                            , 'basin_cd' : 'Drainage basin code'
                            , 'topo_cd' : 'Topographic setting code'
                            , 'instruments_cd' : 'Flags for instruments at site'
                            , 'construction_dt' : 'Date of first construction'
                            , 'inventory_dt' : 'Date site established or inventoried'
                            , 'drain_area_va' : 'Drainage area'
                            , 'contrib_drain_area_va' : 'Contributing drainage area'
                            , 'tz_cd' : 'Time Zone abbreviation'
                            , 'local_time_fg' : 'Site honors Daylight Savings Time'
                            , 'reliability_cd' : 'Data reliability code'
                            , 'gw_file_cd' : 'Data-other GW files'
                            , 'nat_aqfr_cd' : 'National aquifer code'
                            , 'aqfr_cd' : 'Local aquifer code'
                            , 'aqfr_type_cd' : 'Local aquifer type code'
                            , 'well_depth_va' : 'Well depth'
                            , 'hole_depth_va' : 'Hole depth'
                            , 'depth_src_cd' : 'Source of depth data'
                            , 'project_no' : 'Project number'})
    return df

def get_snotel_stations_meta(station_list):
    result = client.service.getStationMetadataMultiple(station_list)
    result = zeep.helpers.serialize_object(result)
    df = pd.DataFrame.from_dict(result)
    return df

def get_snotel_elements(station_list):
    wcc_siteelements = {}
    for station in station_list:
        result = client.service.getStationElements(stationTriplet=station)
        result = zeep.helpers.serialize_object(result)
        df = pd.DataFrame.from_dict(result)
        wcc_siteelements[station] = df
    return wcc_siteelements

# function for getting daily USGS discharge data
def usgs_iv_data(stationID):
    df = nwis.get_record(sites=str(stationID), service='iv', start='1900-10-01', parameterCd='00060')
    if len(df) == 0:
        return df
        
    df = df.reset_index()
    df = df.rename(columns={'00060':'DataValue', 'datetime':'LocalDateTime'})
    df = df.drop(columns=[col for col in df if col not in ['DataValue', 'LocalDateTime']])
    df['LocalDateTime'] = pd.to_datetime(df['LocalDateTime'])
    df['LocalDateTime'] = df['LocalDateTime'].dt.tz_localize(None)
    df = df.set_index('LocalDateTime', drop=True)
    df['DataValue'] = df['DataValue'].replace(-999999, np.nan)
    df = df.resample('1D').mean()
    df['LocalDateTime'] = df.index
    df.drop(['LocalDateTime'], axis=1)
    return df

# =============================================================================
# get SNOTEL data
# =============================================================================
snotel = {'823:UT:SNTL':{},'972:UT:SNTL':{},'820:UT:SNTL':{},'634:UT:SNTL':{},
          '763:UT:SNTL':{},'517:UT:SNTL':{},'513:UT:SNTL':{}}

for key in snotel.keys():
    snotel[key] = snotel_data(key)


filename = 'SNOTEL'+str('.pkl')
filepath = os.path.join(directory, filename)
with open(filepath, 'wb') as f:
    pickle.dump(snotel, f) 

# =============================================================================
# get USGS data
# =============================================================================
usgs = {'10109000':[], '10172200':[], '10164500':[], '10113500':[],
        '10128500':[], '10011500':[], '09289500':[]}

for key in usgs.keys():
    usgs[key] = usgs_data(key)



filename = 'USGS'+str('.pkl')
filepath = os.path.join(directory, filename)
with open(filepath, 'wb') as f:
    pickle.dump(usgs, f) 
