# HTTP Gateway for BLE LEDs

## Running

```bash
sudo hcitool lescan  # Look for something like ELK-BLEDOB. Copy the MAC address
BLE_ADDRESS="BE:60:C3:00:12:4E" python -m quart --app led run --host 0.0.0.0
```

## Home Assistant Setup

In your `configuration.yaml`, add:

```yaml
rest_command:
  led_strip_foo:
    url: "http://YOUR_SERVER_HOSTNAME.lan:5000/{{ mode }}/{{ value }}"
```

and

```yaml
light:
  - platform: template
    lights:
      foo_led_strip:
        friendly_name: Whatever you want
        turn_on:
          service: rest_command.led_strip_foo
          data:
            mode: power
            value: "on"
        turn_off:
          service: rest_command.led_strip_foo
          data:
            mode: power
            value: "off"
        set_level:
          service: rest_command.led_strip_foo
          data:
            mode: brightness
            value: "{{ '%02d'|format(brightness * 100 / 255|int) }}"
        set_rgb:
          service: rest_command.led_strip_foo
          data:
            mode: color
            value: "{{ '%02x' | format(r) }}{{ '%02x' | format(g) }}{{ '%02x' | format(b) }}"
```

Note that to make the difference more obvious, I named the rest command `led_strip_foo` and the light itself `foo_led_strip`. It's probably better for you to use the same name.
