

# This is the loop that is used to when a map search is prefornmed.
def map_llc_result_to_dictionary_list(land_charge_result):
    """Produce a list of jsonable dictionaries of an alchemy result set

    """
    if not isinstance(land_charge_result, list):
        return list(map(lambda land_charge: land_charge.to_dict(),
                        [land_charge_result]))
    else:
        return list(map(lambda land_charge: land_charge.to_dict(),
                        land_charge_result))


def map_llc_display_result_to_dictionary_list(land_charge_result):
    """Produce a list of jsonable dictionaries of an alchemy result set

    """
    if not isinstance(land_charge_result, list):
        return list(map(lambda land_charge: land_charge.to_display_dict(),
                        [land_charge_result]))
    else:
        return list(map(lambda land_charge: land_charge.to_display_dict(),
                        land_charge_result))


def map_llc_history_result_to_dictionary_list(land_charge_history):
    """Produce a list of jsonable dictionaries of an alchemy result set"""
    if not isinstance(land_charge_history, list):
        return list(map(lambda land_charge: land_charge.to_dict(),
                        [land_charge_history]))
    else:
        return list(map(lambda land_charge: land_charge.to_dict(),
                        land_charge_history))


def map_llc_charge_display_result_to_dictionary_list(land_charge_result):
    """Produce a list of jsonable dictionaries of an alchemy result set


    """
    if not isinstance(land_charge_result, list):
        return list(map(lambda land_charge: land_charge.to_charge_display_dict(),
                        [land_charge_result]))
    else:
        return list(map(lambda land_charge: land_charge.to_charge_display_dict(),
                        land_charge_result))
