import pytest
from openleadr import OpenADRClient
from openleadr import enums

def test_trailing_slash_on_vtn_url():
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost/')
    assert client.vtn_url == 'http://localhost'

def test_wrong_handler_supplied(caplog):
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost')
    client.add_handler('non_existant', print)
    assert ("'handler' must be either on_event or on_update_event") in [rec.message for rec in caplog.records]

def test_invalid_report_name(caplog):
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost')
    with pytest.raises(ValueError):
        client.add_report(callback=print,
                          resource_id='myresource',
                          measurement='voltage',
                          report_name='non_existant')
        # assert (f"non_existant is not a valid report_name. Valid options are "
        #         f"{', '.join(enums.REPORT_NAME.values)}",
        #         " or any name starting with 'x-'.") in [rec.message for rec in caplog.records]

def test_invalid_reading_type():
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost')
    with pytest.raises(ValueError):
        client.add_report(callback=print,
                          resource_id='myresource',
                          measurement='voltage',
                          reading_type='non_existant')
            # assert (f"non_existant is not a valid reading_type. Valid options are "
            # f"{', '.join(enums.READING_TYPE.values)}",
            # " or any name starting with 'x-'.") in [rec.message for rec in caplog.records]

def test_invalid_report_type():
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost')
    with pytest.raises(ValueError):
        client.add_report(callback=print,
                          resource_id='myresource',
                          measurement='voltage',
                          report_type='non_existant')
        # assert (f"non_existant is not a valid report_type. Valid options are "
        #         f"{', '.join(enums.REPORT_TYPE.values)}",
        #         " or any name starting with 'x-'.") in [rec.message for rec in caplog.records]

def test_invalid_data_collection_mode():
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost')
    with pytest.raises(ValueError):
        client.add_report(callback=print,
                          resource_id='myresource',
                          measurement='voltage',
                          data_collection_mode='non_existant')
        # assert ("The data_collection_mode should be 'incremental' or 'full'.") in [rec.message for rec in caplog.records]

def test_invalid_scale():
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost')
    with pytest.raises(ValueError):
        client.add_report(callback=print,
                          resource_id='myresource',
                          measurement='voltage',
                          scale='non_existant')

def test_add_report_without_specifier_id():
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost')
    client.add_report(callback=print,
                      resource_id='myresource1',
                      measurement='voltage')
    client.add_report(callback=print,
                      resource_id='myresource2',
                      measurement='voltage')
    assert len(client.reports) == 1

async def wrong_sig(param1):
    pass

def test_add_report_with_invalid_callback_signature():
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost')
    with pytest.raises(TypeError):
        client.add_report(callback=wrong_sig,
                          data_collection_mode='full',
                          resource_id='myresource1',
                          measurement='voltage')
