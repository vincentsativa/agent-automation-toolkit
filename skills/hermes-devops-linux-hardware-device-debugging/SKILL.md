---
name: linux-hardware-device-debugging
title: Linux Hardware Device Debugging
description: "Use when a hardware/network device won't show up on Linux."
version: 1.0.0
created: 2026-08-07
---

# Linux Hardware Device Debugging

## The Core Rule (learned the hard way)

**NEVER declare a device "doesn't exist on this machine" from current enumeration alone.**
`lspci`, `lsusb`, `sysfs`, and ACPI tables only show what enumerated on THIS boot. A
device that fails PCIe link-training on the current boot is completely invisible to all
of them, yet it physically exists and may have worked for weeks.

Real failure this lesson came from: the agent told a user their wired NIC "didn't exist"
repeatedly, citing `lspci` (no ethernet controller), `lsusb` (no adapter), and ACPI HIDs
(no NIC). The user insisted it had worked for weeks. The agent was wrong. The persistent
**kernel journal history** held the truth:

```
Aug 01 06:19:17 kernel: r8169 0000:03:00.0 eth0: RTL8106e, 3c:52:82:8d:b1:71, XID 449, IRQ 32
Aug 01 06:19:17 kernel: r8169 0000:03:00.0 enp3s0: renamed from eth0
```

The NIC existed (Realtek RTL8106e at `0000:03:00.0`) and worked days earlier. It was
invisible on this boot because the PCIe link to it failed to train. Declaring absence off
live enumeration destroyed trust and was wrong.

## When to Use

Trigger on: "wired connection not working", "ethernet/NIC missing", "USB device not
detected", "device not showing up", "hardware not found", any Linux device-presence or
connectivity complaint.

## Evidence-Gathering Order (Phase 1, do in order, STOP once you have proof)

1. **`ls /sys/class/net/`**, live network interfaces.
2. **`lspci`** and **`lspci -nnk`**, current PCI devices, drivers in use, unbound modules.
3. **`lsusb` / `lsusb -t`**, current USB devices (incl. USB ethernet adapters).
4. **`journalctl -k | grep -iE 'r8169|eth0|enp|enx|RTL8|...'`**, KERNEL LOG HISTORY.
   **This is the one that catches devices that enumerated on EARLIER boots but not now.**
   `dmesg` shows only the current boot; `journalctl -k` (persistent journal) shows history.
5. **`journalctl | grep -iE 'enx|eth0|r8169'`**, userspace history (NetworkManager,
   netplan). A stale `netplan-enp3s0` connection in `nmcli con show` also proves the NIC
   previously existed.
6. ONLY after #1–5 show nothing should you say "no such hardware", and even then frame it
   as "not present on this boot", never "doesn't exist".

## Interpreting a Missing-Device Scenario

If a device's PCIe bridge/root-port (e.g. `00:02.5`) is absent from `lspci` and its
`SltSta` shows `PresDet-` / `LinkState-`, the PCIe link failed to train at the
hardware/firmware level. Software cannot create a bridge that isn't enumerating:

- `echo 1 | sudo tee /sys/bus/pci/rescan` (or per-bridge
  `/sys/bus/pci/devices/0000:00:02.1/rescan`), worth one shot; often a no-op if the
  bridge itself is gone.
- `sudo modprobe <driver>`, driver loads but has nothing to bind to if the device isn't
  in the PCI tree. This is EXPECTED and confirms the problem is above the driver, not a
  driver issue.
- A clean **reboot** is the first real fix for flaky PCIe link-training (known on some
  AMD boards).
- If reboot doesn't fix: **reset BIOS to defaults**, check for an "Onboard LAN"/"LAN
  Controller" firmware toggle, then **update BIOS** (link-training bugs are commonly
  firmware-fixed).
- Final resort: the NIC/lane physically failed, hardware repair or a USB ethernet
  adapter. If the user objects to spending money, WiFi may be an acceptable fallback.

## ACPI Firmware Disassembly (when enumeration fails)

When a NIC is defined in firmware but not enumerating, disassemble the DSDT to trace it:

```bash
sudo apt-get install -y acpica-tools        # iasl, acpidump, acpixtract
sudo acpidump -o /tmp/acpi.dat
sudo acpixtract /tmp/acpi.dat               # writes DSDT.dat, SSDT*.dat
sudo iasl -d /tmp/dsdt.dat                  # -> /tmp/dsdt.dsl (disassembled)
grep -niE "LANS|GPP[0-9]|8106|8168|onboard.*lan|_HID|_STA" dsdt.dsl
# Find the NIC's bridge Device block, read its _ADR to map to PCI dev/fn.
```

This traced the RTL8106e's bridge to PCI dev 2 fn 5 (`GPP3`, `_ADR 0x00020005`), which was
absent from the live PCI tree, the whole branch hosting the NIC never enumerated.

## Pitfall: Misreading ACPI `LANS` variables

An ACPI `LANS` variable near the NIC block is often just a **wake-flag** (`_PSW` toggles
wake-on-LAN), NOT the device's present state. Do not misread it as the NIC being disabled.
Check `_ADR`/`_STA` of the actual PCIe bridge device instead.

## Pitfall: The Consensus Lie + premature absence verdict

When a user insists hardware exists and has worked before, treat their word as evidence
and immediately check `journalctl` history BEFORE re-asserting absence. Declaring "there
is no X on this machine" off live enumeration alone, while the kernel log shows X working
days prior, is wrong and destroys trust.
