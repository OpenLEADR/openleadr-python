  {% if event_signal.measurement %}
  <{% if event_signal.measurement.item_name == 'customUnit' %}oadr{% else %}power{% endif %}:{{ event_signal.measurement.item_name }} xmlns:scale="http://docs.oasis-open.org/ns/emix/2011/06/siscale" xmlns:power="http://docs.oasis-open.org/ns/emix/2011/06/power" >
    <{% if event_signal.measurement.item_name == 'customUnit' %}oadr{% else %}power{% endif %}:itemDescription>{{ event_signal.measurement.item_description }}</{% if event_signal.measurement.item_name == 'customUnit' %}oadr{% else %}power{% endif %}:itemDescription>
    <{% if event_signal.measurement.item_name == 'customUnit' %}oadr{% else %}power{% endif %}:itemUnits>{{ event_signal.measurement.item_units }}</{% if event_signal.measurement.item_name == 'customUnit' %}oadr{% else %}power{% endif %}:itemUnits>
    <scale:siScaleCode>{{ event_signal.measurement.si_scale_code }}</scale:siScaleCode>
    {% if event_signal.measurement.power_attributes %}
    <power:powerAttributes>
      <power:hertz>{{ event_signal.measurement.power_attributes.hertz }}</power:hertz>
      <power:voltage>{{ event_signal.measurement.power_attributes.voltage }}</power:voltage>
      <power:ac>{{ event_signal.measurement.power_attributes.ac|booleanformat }}</power:ac>
    </power:powerAttributes>
    {% endif %}
  </{% if event_signal.measurement.item_name == 'customUnit' %}oadr{% else %}power{% endif %}:{{ event_signal.measurement.item_name }}>
  {% endif %}