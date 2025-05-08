from enum import Enum


class TargetType(Enum):
    """Enumeration of target types."""

    POWER_SERVICE_LOCATION = "POWER_SERVICE_LOCATION"
    """
    A Power Service Location is a utility named specific location in geography or
    the distribution system, usually the point of service to a customer site.
    """
    SERVICE_AREA = "SERVICE_AREA"
    """
    A Service Area is a utility named geographic region.
    Target values array contains a string representing a service area name.
    """
    GROUP = "GROUP"
    """
    Target values array contains a string representing a group.
    """
    RESOURCE_NAME = "RESOURCE_NAME"
    """
    Target values array contains a string representing a resource name.
    """
    VEN_NAME = "VEN_NAME"
    """
    Target values array contains a string representing a VEN name.
    """
    EVENT_NAME = "EVENT_NAME"
    """
    Target values array contains a string representing an event name.
    """
    PROGRAM_NAME = "PROGRAM_NAME"
    """
    Target values array contains a string representing a program name.
    """
