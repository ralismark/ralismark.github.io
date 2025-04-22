---
layout: post
title: "BlueHID Details #3: Finally, Controls!"
excerpt: Finally sending inputs over bluetooth
date: 2019-01-13
tags:
series: bluehid
---

After part 1 and 2, we've got everything (finally) set up implement a Bluetoooth HID device.
All we need to do now is to send the control inputs to the connected device, and it's much simpler than setting things up.

<!--more-->

[*Code on github*][ralismark/bluehid].

[ralismark/bluehid]: https://github.com/ralismark/bluehid

I'm going to skip past the code required to get inputs from the user, such as buttons, joysticks, etc.
as it will probably be specific to your purpose.
Look at the source code if you want to know more about how it's implemented in BlueHID.

# Sending inputs

The relevant API for sending a report is [`BluetoothHidDevice.sendReport`][sendreport], which takes the `BluetoothDevice` you're sending the inputs (which should have been previously connected), the report id (0 if you don't use a report id), and the actual report data.
The first two arguments are quite simple, and the report data should follow your report descriptor - which shouldn't be too complicated if you've looked into HID report descriptors e.g.
in the tutorial I linked in the previous part.
Still, I'll go through the one used in BlueHID.

[sendreport]: https://developer.android.com/reference/android/bluetooth/BluetoothHidDevice.html#sendReport(android.bluetooth.BluetoothDevice,%20int,%20byte[])

If you're familiar with HID reports, this is the end!
Send a report when your input change, and things should work out.

# A BlueHID example

I'll explain how this works using the BlueHID report descriptor (even though I said I wouldn't in the previous part).
Most of this doesn't use actual HID terminology, so don't rely on it for that.

```java
0x05, 0x01,        // USAGE_PAGE (Generic Desktop)
0x09, 0x05,        // USAGE (Game Pad)
(byte) 0xa1, 0x01, // COLLECTION (Application)
(byte) 0xa1, 0x00, //   COLLECTION (Physical)
```

This is essentially boilerplate to declare that the device is a gamepad:

```java
0x05, 0x09,        //     USAGE_PAGE (Button)
0x19, 0x01,        //     USAGE_MINIMUM (Button 1)
0x29, 0x04,        //     USAGE_MAXIMUM (Button 4)
0x15, 0x00,        //     LOGICAL_MINIMUM (0)
0x25, 0x01,        //     LOGICAL_MAXIMUM (1)
0x75, 0x01,        //     REPORT_SIZE (1)
(byte) 0x95, 0x04, //     REPORT_COUNT (4)
(byte) 0x81, 0x02, //     INPUT (Data,Var,Abs)
```

This describes a set of 4 buttons (indicated by the usage minimum/maximum).
Each can either be pressed (a value of 1) or not (value of 0), giving us the logical maximum/minimum.
Each button takes up 1 bit (report size), and there are 4 of them (report count).
The input statement ends this block.

```java
0x75, 0x04,        //     REPORT_SIZE (4)
(byte) 0x95, 0x01, //     REPORT_COUNT (1)
(byte) 0x81, 0x03, //     INPUT (Cnst,Var,Abs)
```

This is padding (constant) of 4 bits, ensuring that subsequent values are aligned on byte boundaries.

```java
0x05, 0x01,        //     USAGE_PAGE (Generic Desktop)
0x09, 0x30,        //     USAGE (X)
0x09, 0x31,        //     USAGE (Y)
0x15, (byte) 0x81, //     LOGICAL_MINIMUM (-127)
0x25, 0x7f,        //     LOGICAL_MAXIMUM (127)
0x75, 0x08,        //     REPORT_SIZE (8)
(byte) 0x95, 0x02, //     REPORT_COUNT (2)
(byte) 0x81, 0x02, //     INPUT (Data,Var,Abs)
```

This declares a joystick with a position described by X and Y coordinates.
Each value is stored in 8 bits, and there are 2 of them.
These vary between -127 and 127 (the maximum in a byte[^1]).

[^1]: Yes, technically we can have -128 as a possible value, but excluding it makes the bounds symmetric. This is also what's used in many example descriptors.

```java
(byte) 0xc0,       //   END_COLLECTION
(byte) 0xc0        // END_COLLECTION
```

This finishes the descriptor.

From this, we can determine the format of the report:

{# TODO boxed tables? #}
<table style="table-layout: fixed">
<thead>
	<tr><th>bit</th><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th></th></tr>
</thead>
<tbody>
	<tr><td>Byte 0</td><td class="boxed" colspan="4"><em>padding</em></td><td class="boxed">b4</td><td class="boxed">b3</td><td class="boxed">b2</td><td class="boxed">b1</td><td>(buttons)</td></tr>
	<tr><td>Byte 1</td><td class="boxed" colspan="8">X Axis</td><td></td></tr>
	<tr><td>Byte 2</td><td class="boxed" colspan="8">Y Axis</td><td></td></tr>
</tbody>
</table>

If we fill in the report according to this format (see code for how this can be done), and send it with `sendReport()` whenever the input change, it'll work.

# Bluetooth Issues

After this, the HID controller should work.
However, in practice it may not.
I've experienced significant variation in latency - on some days, it works well, but on others, it just doesn't.
I'm not sure if this is due to the app or the Bluetooth implementation on Android, but I'm pretty sure the app is okay.
You might want to try messing with QoS (the `null` parameters from before), but beyond that, I don't know.
