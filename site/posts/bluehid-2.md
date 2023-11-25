---
layout: post
title: "BlueHID Details #2: What The Heck Is A HID Descriptor"
excerpt: Figuring out how to make a useful HID descriptor
date: 2019-01-07
tags:
---

Now that we've got our Bluetooth HID support up (either through part 1 or by being on P), it's time to start using the API.
At the beginning it's like another Bluetooth profile, but things start get much worse (if you're new to the HID specification) as you get deep into the implementation.

<!--more-->

As always, the final code is available on github at [ralismark/bluehid].

[ralismark/bluehid]: https://github.com/ralismark/bluehid

# Getting ready for HID

We need to first set up Bluetooth and get the appropriate profile, as you would for any profile.
Initially, you need to get the Bluetooth adapter and enable Bluetooth if it's not already.
Then, you need to get a paired device, either through discovery or from existing paired devices (whatever is appropriate).
This is described well and in detail in the [Bluetooth Overview][bt-overview], so I won't repeat what's there.

[bt-overview]: https://developer.android.com/guide/topics/connectivity/bluetooth

Afterwards, you need to get the proxy -- `BluetoothHidDevice` or `BluetoothInputHost` (depending on API level) -- to be able to communicate with the HID service we previously enabled.
This is done with [`BluetoothAdapter.getProfileProxy()`][getprofileproxy].

[getprofileproxy]: https://developer.android.com/reference/android/bluetooth/BluetoothAdapter#getProfileProxy(android.content.Context,%20android.bluetooth.BluetoothProfile.ServiceListener,%20int)

```java
private BluetoothAdapter mBtAdapter; // obtained as you normally would
private BluetoothInputHost mBtHidDevice;

...

mBtAdapter.getProfileProxy(this, new BluetoothProfile.ServiceListener() {
	@Override
	public void onServiceConnected(int profile, BluetoothProfile proxy) {
		if (profile == BluetoothProfile.INPUT_HOST) {
			Log.d(TAG, "Got HID device");
			mBtHidDevice = (BluetoothInputHost) proxy;

			// see next section
			registerApp();
		}
	}

	@Override
	public void onServiceDisconnected(int profile) {
		if (profile == BluetoothProfile.INPUT_HOST) {
			Log.d(TAG, "Lost HID device");
		}
	}
}, BluetoothProfile.INPUT_HOST);
```

This call essentially requests the proxy and saves it.
I've extracted the code to setup Bluetooth HID into `registerApp()`, which we'll see next.

If this is never called, it probably means that the service is not enabled.
Check the previous post on how to do this in Oreo.
I don't have experience with P, so I can't help you if you have this issue there.

# Into HID Hell

After this, if you look around the documentation for `BluetoothHidDevice`, you'll see that you need to register your app.
You reach [`registerApp()`][registerapp], then recoil in horror at the signature:

[registerapp]: https://developer.android.com/reference/android/bluetooth/BluetoothHidDevice#registerApp(android.bluetooth.BluetoothHidDeviceAppSdpSettings,%20android.bluetooth.BluetoothHidDeviceAppQosSettings,%20android.bluetooth.BluetoothHidDeviceAppQosSettings,%20java.util.concurrent.Executor,%20android.bluetooth.BluetoothHidDevice.Callback)

```java
public boolean registerApp(
	BluetoothHidDeviceAppSdpSettings sdp,
	BluetoothHidDeviceAppQosSettings inQos,
	BluetoothHidDeviceAppQosSettings outQos,
	Executor executor,
	BluetoothHidDevice.Callback callback
)
```

Fortunately, after looking at the description, we see we can ignore 2 of these parameters -- `inQos` and `outQos` -- and just set them to `null`.
Another -- `executor` -- is also not present in Oreo, leaving us with `sdp` and `callback`.
Diving into `BluetoothHidDeviceAppSdpSettings` (what a mouthful), we see several arguments in its constructor, including a link to [USB Device Class Definition for HIDs -- firmware specification][hid111].
Read this well and get to understand the required sections, since it's essential to everything from here on out.

[hid111]: https://www.usb.org/sites/default/files/documents/hid1_11.pdf

Now, back to the constructor:

```java
public BluetoothHidDeviceAppSdpSettings(
	String name,
	String description,
	String provider,
	byte subclass,
	byte[] descriptors
)
```

`name`, `description` and `provider` are easy -- you can put pretty much any string for these.
`subclass` isn't too bad either after looking at the spec -- there's only two: none and boot device.
We simply specify none (a single `0x00` byte) and move on, reaching `descriptor` and become confused.

This is the hell of HID hell.
I'm calling it that for a variety of reasons:

- It took me a while to understand this, so it was "hell" personally for me.
	For instance, just determining `bDescriptorType` took a me few hours.
- The documentation is sometimes unclear.
- It appears that no-one has used BluetoothHidDevice yet.

# Through HID Hell

The `descriptor` is made up of the main HID descriptor, followed (literally concatenated) by any other descriptors.
This is the layout of the main descriptor, with unnecessary parts removed (we only need one extra descriptor, and fields for further ones are optional).

| Part                | Byte(s) | Description                                                                     |
| ------------------- | ------- | ------------------------------------------------------------------------------- |
| `bLength`           | 0       | Length of main descriptor (not including other descriptor) -- `0x09`            |
| `bDescriptorType`   | 1       | HID descriptor type -- `0x21`[^2]                                               |
| `bcdHID`            | 2-3     | HID specification version, in little endian binary coded decimal -- `0x11 0x01` |
| `bCountryCode`      | 4       | Country code -- `0x00` for not localised (only relevant for keyboards)          |
| `bNumDescriptors`   | 5       | Number of extra descriptors -- `0x01` (the report descriptor)                   |
| `bDescriptorType`   | 6       | Report type `0x22`[^2]                                                          |
| `wDescriptorLength` | 7-8     | Length of the report descriptor type, in little endian                          |

[^2]: See top of page 49 of the specification.

It turns out, many of these values will always be the same.
After this block in `descriptor`, you append the report descriptor, which describes the "device interface" -- what inputs it has (e.g. buttons, joysticks, magic carpet controls[^3]), what data it can receive (e.g. force feedback, which is extremely complicated to implement), and what other features it supports.
The majority of the HID specification describes this and it somewhat complex representation.
Fortunately, there's [HID descriptor tool][descriptor-tool] to generate this, and plenty of resources online on the content of the actual descriptor, so I won't go into detail (again).
One helpful site is this [tutorial about USB HID report descriptors][hid-tutorial], which provides an example for a device with a joystick and a gamepad with 20 buttons.
Use the descriptor tool to generate the bytes making up the descriptor from the individual items.

[^3]: [HID Usage Tables](https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf), page 42

[descriptor-tool]: https://www.usb.org/document-library/hid-descriptor-tool

[hid-tutorial]: https://eleccelerator.com/tutorial-about-usb-hid-report-descriptors/

Note that there can be multiple reports described, each with a different report ID (this will matter later), but we only have a single.
Take the size of this report, and fill in `wDescriptorLength` in the main descriptor.
Concatenate the two, and you get the `descriptor` argument:

```java
private static final byte[] descriptor = new byte[] {
	// HID descriptor
	0x09, // bLength
	0x21, // bDescriptorType
	0x11, 0x01, // bcdHID
	0x00, // bCountryCode
	0x01, // bNumDescriptors
	0x22, // bDescriptorType
	0x30, 0x00, // wDescriptorLength (48 in decimal)

	// Report descriptor - 4 buttons, 1 X/Y joystick
	0x05, 0x01,        // USAGE_PAGE (Generic Desktop)
	0x09, 0x05,        // USAGE (Game Pad)
	(byte) 0xa1, 0x01, // COLLECTION (Application)
	(byte) 0xa1, 0x00, //   COLLECTION (Physical)
	0x05, 0x09,        //     USAGE_PAGE (Button)
	0x19, 0x01,        //     USAGE_MINIMUM (Button 1)
	0x29, 0x04,        //     USAGE_MAXIMUM (Button 4)
	0x15, 0x00,        //     LOGICAL_MINIMUM (0)
	0x25, 0x01,        //     LOGICAL_MAXIMUM (1)
	0x75, 0x01,        //     REPORT_SIZE (1)
	(byte) 0x95, 0x04, //     REPORT_COUNT (4)
	(byte) 0x81, 0x02, //     INPUT (Data,Var,Abs)
	0x75, 0x04,        //     REPORT_SIZE (4)
	(byte) 0x95, 0x01, //     REPORT_COUNT (1)
	(byte) 0x81, 0x03, //     INPUT (Cnst,Var,Abs)
	0x05, 0x01,        //     USAGE_PAGE (Generic Desktop)
	0x09, 0x30,        //     USAGE (X)
	0x09, 0x31,        //     USAGE (Y)
	0x15, (byte) 0x81, //     LOGICAL_MINIMUM (-127)
	0x25, 0x7f,        //     LOGICAL_MAXIMUM (127)
	0x75, 0x08,        //     REPORT_SIZE (8)
	(byte) 0x95, 0x02, //     REPORT_COUNT (2)
	(byte) 0x81, 0x02, //     INPUT (Data,Var,Abs)
	(byte) 0xc0,       //   END_COLLECTION
	(byte) 0xc0        // END_COLLECTION
};
```

> Since the descriptor describes the format of each report (a update on the inputs), I'll talk more about what the descriptor specifies in the next post where we communicate with the host.

This is the final argument of the `BluetoothHidDeviceAppSdpSettings` constructor, filling in the `sdp` argument of `registerApp()`.

# A Brief Break

This leaves one argument left -- `callback`.
This is fortunately relatively straightforward.
It turns out that `BluetoothHidDevice.Callback` actually has no abstract methods, and the ones handling requests (e.g. `getReport`) are not required (from my experience), so *technically* you can just not do anything.
However, it's helpful to implement `onConnectionStateChanged` to be able to know when the connection is ready and when it has ended.

And with this we are able to finally register our app and connect our device:

```java
BluetoothHidDeviceAppSdpSettings sdp = new BluetoothHidDeviceAppSdpSettings(
	"BlueHID",
	"Android HID hackery",
	"Android",
	(byte) 0x00,
	descriptor
);

mBtHidDevice.registerApp(sdp, null, null, new BluetoothHidDeviceCallback() {
	... // omitted
});

mBtHidDevice.connect(device);
```

This is where I'll end this post, leaving the actual communication to the next one.
There's not much left, and the hardest part of this entire process (working out the descriptor) is now past us, so the final part of this series shouldn't be too hard.

> Final code is available on github at [ralismark/bluehid].

[ralismark/bluehid]: https://github.com/ralismark/bluehid
