# OpenHAB python rule engine
A Python 3.x rule engine for OpenHAB. This rule engine allows you to define rules using Python 3.x. 

**Please note that [OpenHAB username/password authentication](https://www.openhab.org/docs/configuration/restdocs.html) (basic authentication)
must be activated**. To do so, open [API security settings](doc/api_settings.png) and enable the advanced setting [Allow Basic Authentication](doc/basic_auth.png).

To run this software, you can use Docker or the [PIP](https://realpython.com/what-is-pip/) package manager, as shown below

**Docker approach**
```
sudo docker run -e openhab_uri=http://192.168.1.17:8080 -e user=me -e pwd=secret -v /etc/openhab2/automation/rules/python:/rules grro/pythonrule_engine 
```

**PIP approach**
```
sudo pip install openhab-pythonrule-engine
```

```
sudo pyrule --command listen --openhab_uri http://localhost:8080 --python_rule_directory /etc/openhab2/automation/rules/python --user me --pwd secret
```
In this case, the rules engine connects to the Openhab instance running on the local machine on port 8080. Also, the /etc/openhab2/automation/rules/python directory is used to search for python-based rules

If you are using a *systemd-based Linux distribution*, you can use the *register* command to register and start the rule engine as a systemd entity.
This automatically starts the rule engine at boot time. Starting the Rule Engine manually with the *listen* command is no longer necessary.
```
sudo pyrule --command register --openhab_uri http://localhost:8080 --python_rule_directory /etc/openhab2/automation/rules/python --user me --pwd secret
```  


**Rules**

To trigger a rule method, the **@when** decorator must be used. Currently the conditions listed below are supported

| condition  | example | description  |
|---|---|---|
| *cron* | @when('Time cron */1 * * * *') | fires based on cron expression |
| *item state change* | @when('Item PhoneLisaLastSeen changed')  | fires when the specified Item's State changes |
| *item command* | @when('Item SelectDoorCam received command ON') <br/> @when('Item SelectDoorCam received command OFF') | fires when the specified Item receives a Command |
 

Example: **my_rule.py** (located within /etc/openhab2/automation/rules/python)
```python
from openhab_pythonrule_engine.condition import when
from openhab_pythonrule_engine.item_registry import ItemRegistry


@when("Time cron */1 * * * *") # each minute
@when("Item PhoneLisaLastSeen changed")
@when("Item PhoneTimLastSeen changed")
def update_presence_based_on_phone_seen(item_registry: ItemRegistry):
    last_time_present = item_registry.get_state_as_datetime('LastDateTimePresence')
    for phone_name in item_registry.get_group_membernames('Phones'):
        last_seen = item_registry.get_state_as_datetime(phone_name)
        print(last_seen)
        if last_seen > last_time_present:
            last_time_present = last_seen
    item_registry.set_state('LastDateTimePresence', last_time_present)
    
# uncomment the code below for local debugging
#item_registry = ItemRegistry.new_singleton(openhab_uri="http://192.168.1.27:8080/", user="xxx", pwd="secret")
#update_presence_based_on_phone_seen(item_registry)
```

If the rule method defines a (single!) argument, the item_registry object is automatically injected.
The item_registry object provides methods for getting and setting the item state. When setting the state, the data value
is automatically converted to the item-specific data type