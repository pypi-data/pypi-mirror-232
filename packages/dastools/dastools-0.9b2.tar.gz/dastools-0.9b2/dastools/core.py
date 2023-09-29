from pydantic import BaseModel
from datetime import datetime


class Overview(BaseModel):
    network_code: str
    location: str
    country: str
    principal_investigator_name: str
    principal_investigator_email: str
    principal_investigator_address: str
    point_of_contact: str
    point_of_contact_email: str
    point_of_contact_address: str
    start_datetime: datetime
    end_datetime: datetime
    funding_agency: str
    project_number: str
    digital_object_identifier: str
    purpose_of_data_collection: str
    comment: str


class Interrogator(BaseModel):
    interrogator_id: str
    manufacturer: str
    model: str
    serial_number: str
    firmware_version: str
    comment: str


class Acquisition(BaseModel):
    acquisition_id: str
    interrogator_id: str
    acquisition_start_time: datetime
    acquisition_end_time: datetime
    acquisition_sample_rate: float
    acquisition_sample_rate_unit: str
    gauge_length: float
    gauge_length_unit: str
    unit_of_measure: str
    number_of_channels: int
    spatial_sampling_interval: float
    spatial_sampling_interval_unit: str
    pulse_rate: float
    pulse_rate_unit: str
    pulse_width: float
    pulse_width_unit: str
    comment: str


class ChannelGroup(BaseModel):
    channel_group_id: str
    interrogator_id: str
    acquisition_id: str
    cable_id: str
    fiber_id: str
    coordinate_generation_date: datetime
    coordinate_system: str
    reference_frame: str
    location_method: str
    distance_along_fiber_unit: float
    x_coordinate_unit: str
    uncertainty_in_x_coordinate: float
    uncertainty_in_x_coordinate_unit: str
    y_coordinate_unit: str
    uncertainty_in_y_coordinate: float
    uncertainty_in_y_coordinate_unit: str
    elevation_above_sea_level_unit: str
    uncertainty_in_elevation: float
    uncertainty_in_elevation_unit: str
    depth_below_surface_unit: str
    uncertainty_in_depth: float
    uncertainty_in_depth_unit: str
    strike_unit: str
    uncertainty_in_strike: float
    uncertainty_in_strike_unit: str
    dip_unit: str
    uncertainty_in_dip: float
    uncertainty_in_dip_unit: str
    first_usable_channel_id: str
    last_usable_channel_id: str
    comment: str


class Channel(BaseModel):
    channel_id: str
    channel_group_id: str
    distance_along_fiber: float
    x_coordinate: float
    y_coordinate: float
    elevation_above_sea_level: float
    depth_below_surface: float
    strike: float
    dip: float


class Cable(BaseModel):
    cable_id: str
    cable_bounding_box: list
    cable_owner: str
    cable_installation_date: datetime
    cable_removal_date: datetime
    cable_characteristics: str
    cable_environment: str
    cable_installation_environment: str
    cable_model: str
    cable_outside_diameter: float
    cable_outside_diameter_unit: str
    comment: str


class Fiber(BaseModel):
    fiber_id: str
    cable_id: str
    fiber_geometry: str
    fiber_mode: str
    fiber_refraction_index: float
    fiber_winding_angle: float
    fiber_start_location: float
    fiber_start_location_unit: str
    fiber_end_location: float
    fiber_end_location_unit: str
    fiber_optical_length: float
    fiber_optical_length_unit: str
    fiber_one_way_attenuation: float
    fiber_one_way_attenuation_unit: str
    comment: str
