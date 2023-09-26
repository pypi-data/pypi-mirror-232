from settings_models._combat import SettingsModel, Field


class LaneIdMapping(SettingsModel):
    """
    Settings for mapping our gates to apcoa lanes
    """
    lane_id: int = Field(..., description="Lane id in APCOA Flow")
    gate: str = Field(..., description="Gate id in our system")
    is_exit: bool = Field(..., description="If this gate is an exit in APCOA Flow")
