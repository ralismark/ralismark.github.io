---
layout: post
title: "BlueHID Details #1: Oreo Hacks"
tags:
excerpt: Enabling the Bluetooth HID device API on Oreo
---

The upcoming Android P adds support for using your phone as a Bluetooth HID, allowing you to potentially use it as a keyboard, mouse, or even a gamepad. However, there hasn't really been any examples of its use, so I made one. In this series, I'll break down how I made it work.

However, I don't have Android P, only Oreo. But there is way to do this on Oreo, which I'll explain in this entry.

<!--more-->

> I will be uploading the code to GitHub soon, hopefully in a couple of days - stay tuned for updates.
>
> EDIT: Code uploaded as <https://github.com/ralismark/bluehid>

Despite the interest around the addition [BluetoothHidDevice], there doesn't seem too much interest on actually using it [^1] and implementing a device - probably a combination of P still being in developer preview and the actual API being a bit daunting (we'll get up to that later).

[BluetoothHidDevice]: https://developer.android.com/reference/android/bluetooth/BluetoothHidDevice

[^1]: [How can i use the Bluetooth HID Device profile in Android Pie?](https://stackoverflow.com/q/53555092), with no answers (as of the writing of this).

There has been interest before on using an android phone as a Bluetooth HID device [^2], and there are [successful implementations using BLE][blehid]. However, that approach requires the BLE peripheral feature, which many phones (including mine, a OnePlus X) do not support. After some digging, I found that this was already implemented (but disabled and under a different name) in android O - see [this PR][commit].

[^2]: [Implementation of Bluetooth HID device profile in Android Kitkat](https://stackoverflow.com/q/29406726) and [Android as a bluetooth HID keyboard and mouse](https://stackoverflow.com/q/49189504), for instance.

[blehid]: https://github.com/kshoji/BLE-HID-Peripheral-for-Android

[commit]: https://android-review.googlesource.com/c/platform/packages/apps/Bluetooth/+/203832

 All I need to be able to use this is to enable it, and is quite easy with Xposed. Firstly, you need to set the [flag to enable][flag] it.

 [flag]: https://android.googlesource.com/platform/packages/apps/Bluetooth/+/oreo-release/res/values/config.xml#33

```java
@Override
public void handleInitPackageResources(InitPackageResourcesParam resparam) throws Throwable {
	if (!resparam.packageName.equals("com.android.bluetooth")) {
		return;
	}

	resparam.res.setReplacement("com.android.bluetooth",
		"bool", "profile_supported_hidd", true);
}
```

However, due to [this in AndroidManifest.xml][manifest], and the fact that the manifest only matters when installing the app, you also need to enable to service. This can be done through the package manager API:

[manifest]: https://android.googlesource.com/platform/packages/apps/Bluetooth/+/oreo-release/AndroidManifest.xml#384

```java
@Override
public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) throws Throwable {
	if (!lpparam.packageName.equals("com.android.bluetooth")) {
		return;
	}

	Class<?> adapterApp = XposedHelpers.findClass(
		"com.android.bluetooth.btservice.AdapterApp", lpparam.classLoader);

	XposedBridge.hookAllMethods(adapterApp, "onCreate", new XC_MethodHook() {
		@Override
		protected void afterHookedMethod(MethodHookParam param) throws Throwable {
		Application app = (Application) param.thisObject;

		PackageManager pm = app.getPackageManager();

		ComponentName hidServiceName = new ComponentName(
			"com.android.bluetooth", "com.android.bluetooth.hid.HidDevService");
		pm.setComponentEnabledSetting(hidServiceName,
			PackageManager.COMPONENT_ENABLED_STATE_ENABLED, PackageManager.DONT_KILL_APP);
		}
	});
}
```

After this, the Bluetooth HID service is available, and the API can be used (though with some name changes e.g. `BluetoothHidDevice` → `BluetoothInputHost`) after [making internal/hidden API available][hidden].

[hidden]: https://github.com/anggrayudi/android-hidden-api

In the next part of this, I'll start on the actual implementation of BlueHID.
