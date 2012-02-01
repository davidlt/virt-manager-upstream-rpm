# -*- rpm-spec -*-

%define _package virt-manager
%define _version 0.9.1
%define _release 1
%define virtinst_version 0.600.1

%define qemu_user                  "qemu"
%define preferred_distros          "fedora,rhel"
%define kvm_packages               "qemu-system-x86"
%define libvirt_packages           "libvirt"
%define disable_unsupported_rhel   0
%define default_graphics           "spice"

%define with_guestfs               0
%define with_spice                 1
%define with_tui                   1

# End local config

# This macro is used for the continuous automated builds. It just
# allows an extra fragment based on the timestamp to be appended
# to the release. This distinguishes automated builds, from formal
# Fedora RPM builds
%define _extra_release %{?dist:%{dist}}%{!?dist:%{?extra_release:%{extra_release}}}

Name: %{_package}
Version: %{_version}
Release: %{_release}%{_extra_release}
%define verrel %{version}-%{release}

Summary: Virtual Machine Manager
Group: Applications/Emulators
License: GPLv2+
URL: http://virt-manager.org/
Source0: http://virt-manager.org/download/sources/%{name}/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

# These two are just the oldest version tested
Requires: pygtk2 >= 1.99.12-6
Requires: gnome-python2-gconf >= 1.99.11-7
# This version not strictly required: virt-manager should work with older,
# however varying amounts of functionality will not be enabled.
Requires: libvirt-python >= 0.7.0
# Definitely does not work with earlier due to python API changes
Requires: dbus-python >= 0.61
Requires: dbus-x11
# Might work with earlier, but this is what we've tested
Requires: gnome-keyring >= 0.4.9
# Minimum we've tested with
# Although if you don't have this, comment it out and the app
# will work just fine - keyring functionality will simply be
# disabled
Requires: gnome-python2-gnomekeyring >= 2.15.4
# Minimum we've tested with
Requires: libxml2-python >= 2.6.23
# Absolutely require this version or later
Requires: python-virtinst >= %{virtinst_version}
# Required for loading the glade UI
Requires: pygtk2-libglade
# Earlier vte had broken python binding module
Requires: vte >= 0.12.2
# For online help
Requires: scrollkeeper
# For console widget
Requires: gtk-vnc-python >= 0.3.8
# For local authentication against PolicyKit
# Fedora 12 has no need for a client agent
%if 0%{?fedora} == 11
Requires: PolicyKit-authentication-agent
%endif
%if 0%{?fedora} >= 9 && 0%{?fedora} < 11
Requires: PolicyKit-gnome
%endif
%if %{with_spice}
Requires: spice-gtk-python
%endif
%if %{with_guestfs}
Requires: python-libguestfs
%endif

%if %{with_tui} == 0
Obsoletes: virt-manager-common <= %{verrel}
Conflicts: virt-manager-common > %{verrel}
%else
Requires: virt-manager-common = %{verrel}
%endif

BuildRequires: gettext
BuildRequires: scrollkeeper
BuildRequires: intltool
BuildRequires: GConf2

Requires(pre): GConf2
Requires(post): GConf2
Requires(preun): GConf2
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

%if %{with_spice}
%define default_graphics "spice"
%endif

%description
Virtual Machine Manager provides a graphical tool for administering virtual
machines for KVM, Xen, and QEmu. Start, stop, add or remove virtual devices,
connect to a graphical or serial console, and see resource usage statistics
for existing VMs on local or remote machines. Uses libvirt as the backend
management API.

# TUI package setup
%if %{with_tui}
%package tui
Summary: Virtual Machine Manager text user interface
Group: Applications/Emulators

Requires: virt-manager-common = %{verrel}
Requires: python-newt_syrup >= 0.1.2
Requires: libuser-python
Requires: python-IPy

%description tui
An interactive text user interface for Virtual Machine Manager.

%package common
Summary: Common files used by the different Virtual Machine Manager interfaces
Group: Applications/Emulators

# This version not strictly required: virt-manager should work with older,
# however varying amounts of functionality will not be enabled.
Requires: libvirt-python >= 0.7.0
Requires: dbus-python
# Minimum we've tested with
Requires: libxml2-python >= 2.6.23
# Absolutely require this version or later
Requires: python-virtinst >= %{virtinst_version}

%description common
Common files used by the different Virtual Machine Manager interfaces.
%endif

%prep
%setup -q

%build
%if %{qemu_user}
%define _qemu_user --with-qemu_user=%{qemu_user}
%endif

%if %{kvm_packages}
%define _kvm_packages --with-kvm-packages=%{kvm_packages}
%endif

%if %{preferred_distros}
%define _preferred_distros --with-preferred-distros=%{preferred_distros}
%endif

%if %{libvirt_packages}
%define _libvirt_packages --with-libvirt-package-names=%{libvirt_packages}
%endif

%if %{disable_unsupported_rhel}
%define _disable_unsupported_rhel --disable-unsupported-rhel-options
%endif

%if %{?default_graphics}
%define _default_graphics --with-default-graphics=%{default_graphics}
%endif

%if %{with_tui}
%define _tui_opt --with-tui
%else
%define _tui_opt --without-tui
%endif

%configure  %{?_tui_opt} \
            %{?_qemu_user} \
            %{?_kvm_packages} \
            %{?_libvirt_packages} \
            %{?_preferred_distros} \
            %{?_disable_unsupported_rhel} \
            %{?_default_graphics}
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install  DESTDIR=$RPM_BUILD_ROOT
%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%gconf_schema_prepare %{name}

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
update-desktop-database -q %{_datadir}/applications
%gconf_schema_upgrade %{name}

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
update-desktop-database -q %{_datadir}/applications

%preun
%gconf_schema_remove %{name}

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%if %{with_tui}
%files
%else
%files -f %{name}.lang
%endif
%defattr(-,root,root,-)
%doc README COPYING COPYING-DOCS AUTHORS ChangeLog NEWS
%{_sysconfdir}/gconf/schemas/%{name}.schemas
%{_bindir}/%{name}
%{_libexecdir}/%{name}-launch

%{_mandir}/man1/%{name}.1*

%if %{with_tui} == 0
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/virtManager/
%{_datadir}/%{name}/virtManager/*.py*
%endif

%{_datadir}/%{name}/*.glade
%{_datadir}/%{name}/%{name}.py*

%{_datadir}/%{name}/icons
%{_datadir}/icons/hicolor/*/apps/*

%{_datadir}/applications/%{name}.desktop
%{_datadir}/dbus-1/services/%{name}.service

%if %{with_tui}
%files common -f %{name}.lang
%defattr(-,root,root,-)
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/virtManager/

%{_datadir}/%{name}/virtManager/*.py*

%files tui
%defattr(-,root,root,-)

%{_bindir}/%{name}-tui
%{_datadir}/%{name}/%{name}-tui.py*

%{_datadir}/%{name}/virtManagerTui
%endif

%changelog
* Wed Feb 01 2012 Cole Robinson <crobinso@redhat.com> - 0.9.1-1
- Rebased to version 0.9.1
- Support for adding usb redirection devices (Marc-André Lureau)
- Option to switch usb controller to support usb2.0 (Marc-André Lureau)
- Option to specify machine type for non-x86 guests (Li Zhang)
- Support for filesystem device type and write policy (Deepak C Shetty)
- Many bug fixes!

* Fri Oct 28 2011 Cole Robinson <crobinso@redhat.com> - 0.9.0-7
- Fix crashes when deleting a VM (bz 749263)

* Tue Sep 27 2011 Cole Robinson <crobinso@redhat.com> - 0.9.0-6
- Fix 'Resize to VM' graphical option (bz 738806)
- Fix deleting guest with managed save data
- Fix error when adding default storage
- Don't flush XML cache on every tick
- Use labels for non-editable network info fields (bz 738751)
- Properly update icon cache (bz 733836)

* Tue Aug 02 2011 Cole Robinson <crobinso@redhat.com> - 0.9.0-5
- Fix python-newt_syrup dep

* Mon Aug 01 2011 Cole Robinson <crobinso@redhat.com> - 0.9.0-4
- Don't have a hard dep on libguestfs (bz 726364)
- Depend on needed python-newt_syrup version

* Thu Jul 28 2011 Cole Robinson <crobinso@redhat.com> - 0.9.0-3
- Fix typo that broke net stats reporting
- Add BuildRequires: GConf2 to fix pre scriplet error

* Tue Jul 26 2011 Cole Robinson <crobinso@redhat.com> - 0.9.0-1.fc16
- Rebased to version 0.9.0
- Use a hiding toolbar for fullscreen mode
- Use libguestfs to show guest packagelist and more (Richard W.M. Jones)
- Basic 'New VM' wizard support for LXC guests
- Remote serial console access (with latest libvirt)
- Remote URL guest installs (with latest libvirt)
- Add Hardware: Support <filesystem> devices
- Add Hardware: Support <smartcard> devices (Marc-André Lureau)
- Enable direct interface selection for qemu/kvm (Gerhard Stenzel)
- Allow viewing and changing disk serial number

* Thu Apr 28 2011 Cole Robinson <crobinso@redhat.com> - 0.8.7-5.fc16
- Stop netcf errors from flooding logs (bz 676920)
- Bump default mem for new guests to 1GB so F15 installs work (bz
  700480)

* Tue Apr 19 2011 Cole Robinson <crobinso@redhat.com> - 0.8.7-4.fc16
- Fix spice RPM dependency (bz 697729)

* Thu Apr 07 2011 Cole Robinson <crobinso@redhat.com> - 0.8.7-3.fc16
- Fix broken cs.po which crashed gettext
- Fix offline attach fallback if hotplug fails
- Offer to attach spicevmc if switching to spice

* Thu Mar 31 2011 Cole Robinson <crobinso@redhat.com> - 0.8.7-2.fc16
- Fix using spice as default graphics type
- Fix lockup as non-root (bz 692570)

* Mon Mar 28 2011 Cole Robinson <crobinso@redhat.com> - 0.8.7-1.fc16
- Rebased to version 0.8.7
- Allow renaming an offline VM
- Spice password support (Marc-André Lureau)
- Allow editting NIC <virtualport> settings (Gerhard Stenzel)
- Allow enabling/disabling individual CPU features
- Allow easily changing graphics type between VNC/SPICE for existing VM
- Allow easily changing network source device for existing VM

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Feb  2 2011 Cole Robinson <crobinso@redhat.com> - 0.8.6-1.fc15
- Update to 0.8.6
- SPICE support (requires spice-gtk) (Marc-André Lureau)
- Option to configure CPU model
- Option to configure CPU topology
- Save and migration cancellation (Wen Congyang)
- Save and migration progress reporting
- Option to enable bios boot menu
- Option to configure direct kernel/initrd boot

* Wed Aug 25 2010 Cole Robinson <crobinso@redhat.com> - 0.8.5-1.fc15
- Update to 0.8.5
- Improved save/restore support
- Option to view and change disk cache mode
- Configurable VNC keygrab sequence (Michal Novotny)

* Mon Aug  2 2010 David Malcolm <dmalcolm@redhat.com> - 0.8.4-3.fc15
- fix python 2.7 incompatibility (bz 620216)

* Thu May 27 2010 Cole Robinson <crobinso@redhat.com> - 0.8.4-2.fc14
- Only close connection on specific remote errors
- Fix weird border in manager UI (bz 583728)
- Fix broken icons
- Cancel post-install reboot if VM is forced off
- Fix traceback if customizing a livecd install (bz 583712)
- Add pool refresh button
- Properly autodetect VNC keymap (bz 586201)
- Fix traceback when reconnecting to remote VNC console (bz 588254)
- Fix remote VNC connection with zsh as default shell

* Wed Mar 24 2010 Cole Robinson <crobinso@redhat.com> - 0.8.4-1.fc14
- Update to version 0.8.4
- 'Import' install option, to create a VM around an existing OS image
- Support multiple boot devices and boot order
- Watchdog device support
- Enable setting a human readable VM description.
- Option to manually specifying a bridge name, if bridge isn't detected

* Mon Mar 22 2010 Cole Robinson <crobinso@redhat.com> - 0.8.3-2.fc14
- Fix using a manual 'default' pool (bz 557020)
- Don't force grab focus when app is run (bz 548430)
- Check packagekit for KVM and libvirtd (bz 513494)
- Fake a reboot implementation if libvirt doesn't support it (bz 532216)
- Mark some strings as translatable (bz 572645)

* Mon Feb  8 2010 Cole Robinson <crobinso@redhat.com> - 0.8.3-1.fc13
- Update to 0.8.3 release
- Manage network interfaces: start, stop, view, provision bridges, bonds, etc.
- Option to 'customize VM before install'.

* Tue Jan 12 2010 Cole Robinson <crobinso@redhat.com> - 0.8.2-2.fc13
- Build with actual upstream tarball (not manually built dist)

* Mon Dec 14 2009 Cole Robinson <crobinso@redhat.com> - 0.8.2-1.fc13
- Update to 0.8.2 release
- Fix first virt-manager run on a new install
- Enable floppy media eject/connect

* Wed Dec 09 2009 Cole Robinson <crobinso@redhat.com> - 0.8.1-3.fc13
- Select manager row on right click, regressed with 0.8.1

* Sat Dec  5 2009 Cole Robinson <crobinso@redhat.com> - 0.8.1-2.fc13
- Set proper version Requires: for python-virtinst

* Thu Dec  3 2009 Cole Robinson <crobinso@redhat.com> - 0.8.1-1.fc13
- Update to release 0.8.1
- VM Migration wizard, exposing various migration options
- Enumerate CDROM and bridge devices on remote connections
- Support storage pool source enumeration for LVM, NFS, and SCSI

* Mon Oct 05 2009 Cole Robinson <crobinso@redhat.com> - 0.8.0-8.fc13
- Don't allow creating a volume without a name (bz 526111)
- Don't allow volume allocation > capacity (bz 526077)
- Add tooltips for toolbar buttons (bz 524083)

* Mon Oct 05 2009 Cole Robinson <crobinso@redhat.com> - 0.8.0-7.fc13
- More translations (bz 493795)

* Tue Sep 29 2009 Cole Robinson <crobinso@redhat.com> - 0.8.0-6.fc13
- Fix VCPU hotplug
- Remove access to outdated docs (bz 522823, bz 524805)
- Update VM state text in manager view (bz 526182)
- Update translations (bz 493795)

* Thu Sep 24 2009 Cole Robinson <crobinso@redhat.com> - 0.8.0-5.fc12
- Refresh host disk space in create wizard (bz 502777)
- Offer to fix disk permission issues (bz 517379)

* Thu Sep 17 2009 Cole Robinson <crobinso@redhat.com> - 0.8.0-4.fc12
- Don't close libvirt connection for non-fatal errors (bz 522168)
- Manager UI tweaks
- Generate better errors if disk/net stats polling fails

* Mon Sep 14 2009 Cole Robinson <crobinso@redhat.com> - 0.8.0-3.fc12
- Fix disk XML mangling via connect/eject cdrom (bz 516116)
- Fix delete button sensitivity (bz 518536)
- Fix populating text box from storage browser in 'New VM' (bz 517263)
- Fix a traceback in an 'Add Hardware' error path (bz 517286)

* Thu Aug 13 2009 Daniel P. Berrange <berrange@redhat.com> - 0.8.0-2.fc12
- Remove obsolete dep on policykit agent

* Tue Jul 28 2009 Cole Robinson <crobinso@redhat.com> - 0.8.0-1.fc12
- Update to release 0.8.0
- New 'Clone VM' Wizard
- Improved UI, including an overhaul of the main 'manager' view
- System tray icon for easy VM access (start, stop, view console/details)
- Wizard for adding serial, parallel, and video devices to existing VMs.

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu May 21 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.0-5.fc12
- Fix 'opertaing' typo in 'New VM' dialog (#495128)
- Allow details window to resize again (#491683)
- Handle collecting username for vnc authentication (#499589)
- Actually handle arch config when creating a VM (#499145)
- Log libvirt capabilities at startup to aid debugging (#500337)

* Tue Apr 14 2009 Cole Robinson <crobinso@redhat.com> - 0.7.0-4.fc11
- More translation updates

* Thu Apr 09 2009 Cole Robinson <crobinso@redhat.com> - 0.7.0-3.fc11
- Fix incorrect max vcpu setting in New VM wizard (bz 490466)
- Fix some OK/Cancel button ordering issues (bz 490207)
- Use openAuth when duplicating a connection when deleting a VM
- Updated translations (bz 493795)

* Mon Mar 23 2009 Cole Robinson <crobinso@redhat.com> - 0.7.0-2.fc11
- Back compat fixes for connecting to older xen installations (bz 489885)
- Don't show harmless NoneType error when launching new VM details window

* Tue Mar 10 2009 Cole Robinson <crobinso@redhat.com> - 0.7.0-1.fc11
- Update to release 0.7.0
- Redesigned 'New Virtual Machine' wizard
- Option to remove storage when deleting a virtual machine.
- File browser for libvirt storage pools and volumes
- Physical device assignment (PCI, USB) for existing virtual machines.

* Wed Mar  4 2009 Cole Robinson <crobinso@redhat.com> - 0.6.1-4.fc11
- Update polish translation (bz 263301)
- Fix sending ctrl-alt-del to guest
- Fix cpu + mem stats options to remember preference.

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb  9 2009 Cole Robinson <crobinso@redhat.com> - 0.6.1-2
- Kill off consolehelper (PolicyKit is sufficient)

* Mon Jan 26 2009 Cole Robinson <crobinso@redhat.com> - 0.6.1-1
- Update to 0.6.1 release
- Disk and Network VM stats reporting
- VM Migration support
- Support adding sound devices to existing VMs
- Allow specifying device model when adding a network device to an existing VM

* Tue Jan 20 2009 Mark McLoughlin <markmc@redhat.com> - 0.6.0-7
- Add patch to ignore fix crash on force-poweroff with serial console (#470548)

* Thu Dec 04 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.6.0-6
- Rebuild for Python 2.6

* Mon Dec  1 2008 Cole Robinson <crobinso@redhat.com> - 0.6.0-5.fc10
- Fix spec for building on F9
- Update 'New VM' virt descriptions to be less black and white (bz 470563)

* Sun Nov 30 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.6.0-4
- Rebuild for Python 2.6

* Mon Oct 27 2008 Cole Robinson <crobinso@redhat.com> - 0.6.0-3.fc10
- Add dbus-x11 to Requires (bug 467886)
- Fedora translation updates (bug 467808)
- Don't add multiple sound devices if install fails
- Only popup volume path copy option on right click
- Fix a variable typo

* Tue Oct 14 2008 Cole Robinson <crobinso@redhat.com> - 0.6.0-2.fc10
- Add gnome-python2-gnome requirement.
- Allow seeing connection details if disconnected.
- Updated catalan translation.
- Update dutch translation.
- Update german translation. (bug 438136)
- Fix showing domain console when connecting to hypervisor.
- Update POTFILES to reflect reality (bug 466835)

* Wed Sep 10 2008 Cole Robinson <crobinso@redhat.com> - 0.6.0-1.fc10
- Update to 0.6.0 release
- Add libvirt storage management support
- Basic support for remote guest installation
- Merge VM console and details windows
- Poll avahi for libvirtd advertisement
- Hypervisor autoconnect option
- Add sound emulation when creating new guests

* Thu Apr  3 2008 Daniel P. Berrange <berrange@redhat.com> - 0.5.4-3.fc9
- Updated sr, de, fi, it, pl translations

* Thu Mar 13 2008 Daniel P. Berrange <berrange@redhat.com> - 0.5.4-2.fc9
- Don't run policykit checks when root (rhbz #436994)

* Mon Mar 10 2008 Daniel P. Berrange <berrange@redhat.com> - 0.5.4-1.fc9
- Update to 0.5.4 release

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.5.3-2
- Autorebuild for GCC 4.3

* Thu Jan 10 2008 Daniel P. Berrange <berrange@redhat.com> - 0.5.3-1.fc9
- Update to 0.5.3 release

* Mon Oct 15 2007 Daniel P. Berrange <berrange@redhat.com> - 0.5.2-2.fc8
- Change TLS x509 credential name to sync with libvirt

* Thu Oct  4 2007 Daniel P. Berrange <berrange@redhat.com> - 0.5.2-1.fc8
- Update to 0.5.2 release
- No scrollbars for high res guest in low res host (rhbz 273181)
- Unable to remove network device (rhbz 242900)
- Fixed broken menu items (rhbz 307551)
- Require libvirt 0.3.3 to get CDROM change capability for Xen

* Tue Sep 25 2007 Daniel P. Berrange <berrange@redhat.com> - 0.5.1-1.fc8
- Updated to 0.5.1 release
- Open connections in background
- Make VNC connection retries more robust
- Allow changing of CDROM media on the fly
- Add PXE boot installation of HVM guests
- Allow tunnelling VNC over SSH

* Wed Aug 29 2007 Daniel P. Berrange <berrange@redhat.com> - 0.5.0-1.fc8
- Updated to 0.5.0 release
- Support for managing remote hosts
- Switch to use GTK-VNC for the guest console

* Fri Aug 24 2007 Daniel P. Berrange <berrange@redhat.com> - 0.4.0-3.fc8
- Remove ExcludeArch since libvirt is now available

* Wed May  9 2007 Daniel P. Berrange <berrange@redhat.com> - 0.4.0-2.fc7
- Refresh po file translations (bz 238369)
- Fixed removal of disk/network devices
- Fixed toolbar menu option state
- Fixed file dialogs & default widget states

* Mon Apr 16 2007 Daniel P. Berrange <berrange@redhat.com> - 0.4.0-1.fc7
- Support for managing virtual networks
- Ability to attach guest to virtual networks
- Automatically set VNC keymap based on local keymap
- Support for disk & network device addition/removal

* Wed Mar 28 2007 Daniel P. Berrange <berrange@redhat.com> - 0.3.2-3.fc7
- Fix HVM check to allow KVM guests to be created (bz 233644)
- Fix default file size suggestion

* Tue Mar 27 2007 Daniel P. Berrange <berrange@redhat.com> - 0.3.2-2.fc7
- Ensure we own all directories we create (bz 233816)

* Tue Mar 20 2007 Daniel P. Berrange <berrange@redhat.com> - 0.3.2-1.fc7
- Added online help to all windows
- Bug fixes to virtual console popup, key grab & accelerator override

* Tue Mar 13 2007 Daniel P. Berrange <berrange@redhat.com> - 0.3.1-4.fc7
- Fixed thread locking to avoid deadlocks when a11y is enabled

* Fri Mar  2 2007 Daniel P. Berrange <berrange@redhat.com> - 0.3.1-3.fc7
- Fixed keyboard ungrab in VNC widget

* Tue Feb 20 2007 Daniel P. Berrange <berrange@redhat.com> - 0.3.1-2.fc7
- Only check for HVM on Xen hypervisor

* Tue Feb 20 2007 Daniel P. Berrange <berrange@redhat.com> - 0.3.1-1.fc7
- Added support for managing QEMU domains
- Automatically grab mouse pointer to workaround dual-cursor crazyness

* Wed Jan 31 2007 Daniel P. Berrange <berrange@redhat.com> - 0.3.0-2.fc7
- Added dep on desktop-file-utils for post/postun scripts

* Mon Jan 22 2007 Daniel P. Berrange <berrange@redhat.com> - 0.3.0-1.fc7
- Added support for managing inactive domains
- Require virt-inst >= 0.100.0 and libvirt >= 0.1.11 for ianctive
  domain management capabilities
- Add progress bars during VM creation stage
- Improved reliability of VNC console
- Updated translations again
- Added destroy option to menu bar to forceably kill a guest
- Visually differentiate allocated memory, from actual used memory on host
- Validate file magic when restoring a guest from a savd file
- Performance work on domain listing
- Allow creation of non-sparse files
- Fix backspace key in serial console

* Tue Dec 19 2006 Daniel P. Berrange <berrange@redhat.com> - 0.2.6-3.fc7
- Imported latest translations from Fedora i18n repository (bz 203783)
- Use 127.0.0.1 address for connecting to VNC console instead of
  localhost to avoid some issue with messed up /etc/hosts.
- Add selector for sparse or non-sparse file, defaulting to non-sparse.
  Add appropriate warnings and progress-bar text. (bz 218996)
- Disable memory ballooning & CPU hotplug for HVM guests (bz 214432)
- Updated memory-setting UI to include a hard upper limit for physical
  host RAM
- Added documentation on the page warning that setting virtual host RAM
  too high can exhaust the memory of the machine
- Handle errors when hostname resolution fails to avoid app exiting (bz 216975)

* Thu Dec  7 2006 Jeremy Katz <katzj@redhat.com> - 0.2.6-2.fc7
- rebuild for python 2.5

* Thu Nov  9 2006 Daniel P. Berrange <berrange@redhat.com> - 0.2.6-1.fc7
- Imported translations from Fedora i18n repository
- Make (most) scrollbar policies automatic
- Set busy cursor while creating new VMs
- Preference for controlling keygrab policy
- Preference for when to automatically open console (bz 211385)
- Re-try VNC connection attempt periodically in case VNC daemon
  hasn't finished starting up
- Added activation of URLs for about dialog (bz 210782)
- Improved error reporting when connecting to HV (bz 211229)
- Add command line args to open specific windows
- Don't skip para/full virt wizard step - instead gray out full
  virt option & tell user why
- Change 'physical' to 'logical' when refering to host CPUs
- Include hostname in titlebar
- Disable wizard sensitivity while creating VM

* Thu Oct 19 2006 Daniel P. Berrange <berrange@redhat.com> - 0.2.5-1.fc7
- Switch to use python-virtinst instead of python-xeninst due to 
  renaming of original package
- Disable keyboard accelerators when grabbing mouse to avoid things like
  Ctrl-W closing the local window, instead of remote window bz 210364
- Fix host memory reporting bz 211281
- Remove duplicate application menu entry bz 211230
- Fix duplicated mnemonics (bz 208408)
- Use blktap backed disks if available
- Use a drop down list to remember past URLs (bz 209479)
- Remove unused help button from preferences dialog (bz 209251)
- Fix exception when no VNC graphics is defined
- Force immediate refresh of VMs after creating a new one
- Improve error reporting if run on a kernel without Xen (bz 209122)
- More fixes to avoid stuck modifier keys on focus-out (bz 207949)

* Fri Sep 29 2006 Daniel P. Berrange <berrange@redhat.com> 0.2.3-2.fc6
- Fix segv in sparkline code when no data points are defined (bz  208185)
- Clamp CPU utilization between 0 & 100% just in case (bz 208185)

* Tue Sep 26 2006 Daniel Berrange <berrange@redhat.com> - 0.2.3-1.fc6
- Require xeninst >= 0.93.0 to fix block backed devices
- Skip para/fully-virt step when going back in wizard if not HVM host (bz 207409)
- Fix handling of modifier keys in VNC console so Alt key doesn't get stuck (bz 207949)
- Allow sticky modifier keys by pressing same key 3 times in row (enables Ctrl-Alt-F1
  by doing Ctrl Ctrl Ctrl  Alt-F1)
- Improved error handling during guest creation
- Log errors with python logging, instead of to stdout
- Remove unused buttons from main domain list window
- Switch out of full screen & release key grab when closing console
- Trim sparkline CPU history graph to 40 samples max
- Constraint VCPU adjuster to only allow upto guest's max VCPU count
- Show guest's max & current VCPU count in details page
- Fix rounding of disk sizes to avoid a 1.9 GB disk being rounded down to 1 GB
- Use raw block device path to CDROM not mount point for HVM guest (bz 206965)
- Fix visibility of file size spin box (bz 206186 part 2)
- Check for GTK failing to open X11 display (bz 205938)

* Fri Sep 15 2006 Daniel Berrange <berrange@redhat.com> - 0.2.2-1.fc6
- Fix event handling in create VM wizard (bz 206660 & 206186)
- Fix close button in about dialog (bz 205943)
- Refresh .pot files
- Turn on VNC scrollbars fulltime to avoid GTK window sizing issue
  which consistently resize too small.

* Mon Sep 11 2006 Daniel Berrange <berrange@redhat.com> - 0.2.1-3.fc6
- Added requires on pygtk2-libglade & librsvg2 (bz 205941 & 205942)
- Re-arrange to use console-helper to launch app
- Added 'dist' component to release number

* Wed Sep  6 2006 Jeremy Katz <katzj@redhat.com> - 0.2.1-2
- don't ghost pyo files (#205448)

* Mon Sep  4 2006 Daniel Berrange <berrange@redhat.com> - 0.2.1-1
- Updated to 0.2.1 tar.gz
- Added rules to install/uninstall gconf schemas in preun,post,pre
  scriptlets
- Updated URL for source to reflect new upstream download URL

* Thu Aug 24 2006 Jeremy Katz <katzj@redhat.com> - 0.2.0-3
- BR gettext

* Thu Aug 24 2006 Jeremy Katz <katzj@redhat.com> - 0.2.0-2
- only build on arches with virt

* Tue Aug 22 2006 Daniel Berrange <berrange@redhat.com> - 0.2.0-1
- Added wizard for creating virtual machines
- Added embedded serial console
- Added ability to take screenshots

* Mon Jul 24 2006 Daniel Berrange <berrange@redhat.com> - 0.1.5-2
- Prefix *.pyo files with 'ghost' macro
- Use fully qualified URL in Source  tag

* Thu Jul 20 2006 Daniel Berrange <berrange@redhat.com> - 0.1.5-1
- Update to new 0.1.5 release snapshot

* Thu Jul 20 2006 Daniel Berrange <berrange@redhat.com> - 0.1.4-1
- Update to new 0.1.4 release snapshot

* Mon Jul 17 2006 Daniel Berrange <berrange@redhat.com> - 0.1.3-1
- Fix License tag
- Updated for new release

* Wed Jun 28 2006 Daniel Berrange <berrange@redhat.com> - 0.1.2-3
- Added missing copyright headers on all .py files

* Wed Jun 28 2006 Daniel Berrange <berrange@redhat.com> - 0.1.2-2
- Added python-devel to BuildRequires

* Wed Jun 28 2006 Daniel Berrange <berrange@redhat.com> - 0.1.2-1
- Change URL to public location

* Fri Jun 16 2006 Daniel Berrange <berrange@redhat.com> - 0.1.0-1
- Added initial support for using VNC console

* Thu Apr 20 2006 Daniel Berrange <berrange@redhat.com> - 0.0.2-1
- Added DBus remote control service

* Wed Mar 29 2006 Daniel Berrange <berrange@redhat.com> - 0.0.1-1
- Initial RPM build
