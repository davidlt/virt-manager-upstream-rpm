# -*- rpm-spec -*-

# This macro is used for the continuous automated builds. It just
# allows an extra fragment based on the timestamp to be appended
# to the release. This distinguishes automated builds, from formal
# Fedora RPM builds
%define _extra_release %{?dist:%{dist}}%{!?dist:%{?extra_release:%{extra_release}}}

Name: virt-manager
Version: 0.2.3
Release: 2%{_extra_release}
Summary: Virtual Machine Manager

Group: Applications/Emulators
License: GPL
URL: http://virt-manager.et.redhat.com/
Source0: http://virt-manager.et.redhat.com/download/sources/%{name}/%{name}-%{version}.tar.gz
Source1: %{name}.pam
Source2: %{name}.console
Patch1: %{name}-sparklinesegv.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# These two are just the oldest version tested
Requires: pygtk2 >= 1.99.12-6
Requires: gnome-python2-gconf >= 1.99.11-7
# Absolutely require this version or newer
Requires: libvirt-python >= 0.1.4-3
# Definitely does not work with earlier due to python API changes
Requires: dbus-python >= 0.61
# Might work with earlier, but this is what we've tested
Requires: gnome-keyring >= 0.4.9
# Minimum we've tested with
# Although if you don't have this, comment it out and the app
# will work just fine - keyring functionality will simply be
# disabled
Requires: gnome-python2-gnomekeyring >= 2.15.4
# Minimum we've tested with
Requires: libxml2-python >= 2.6.23
# Required to install Xen guests
Requires: python-xeninst >= 0.93.0
# Required for loading the glade UI
Requires: pygtk2-libglade
# Required for our graphics which are currently SVG format
Requires: librsvg2
# Earlier vte had broken python binding module
Requires: vte >= 0.12.2
# For the consolehelper PAM stuff
Requires: usermode

ExclusiveArch: %{ix86} x86_64 ia64

BuildRequires: pygtk2-devel
BuildRequires: gtk2-devel
BuildRequires: python-devel
BuildRequires: gettext

Requires(pre): GConf2
Requires(post): GConf2
Requires(preun): GConf2

%description
Virtual Machine Manager provides a graphical tool for administering
virtual machines such as Xen. It uses libvirt as the backend management
API.

%prep
%setup -q
%patch1 -p1

%build
%configure
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install  DESTDIR=$RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}/sparkline.a
rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}/sparkline.la

# Adjust for console-helper magic
mkdir -p $RPM_BUILD_ROOT%{_sbindir}
mv $RPM_BUILD_ROOT%{_bindir}/%{name} $RPM_BUILD_ROOT%{_sbindir}/%{name}
ln -s %{_bindir}/consolehelper $RPM_BUILD_ROOT%{_bindir}/%{name}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pam.d
cp %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/%{name}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/security/console.apps
cp %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/security/console.apps/%{name}

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ "$1" -gt 1 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
      %{_sysconfdir}/gconf/schemas/%{name}.schemas > /dev/null || :
fi

%post
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule \
  %{_sysconfdir}/gconf/schemas/%{name}.schemas > /dev/null || :

update-desktop-database %{_datadir}/applications

%postun
update-desktop-database %{_datadir}/applications

%preun
if [ "$1" -eq 0 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
      %{_sysconfdir}/gconf/schemas/%{name}.schemas > /dev/null || :
fi

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc README COPYING AUTHORS ChangeLog NEWS
%{_sysconfdir}/gconf/schemas/%{name}.schemas
%{_sysconfdir}/pam.d/%{name}
%{_sysconfdir}/security/console.apps/%{name}
%{_bindir}/%{name}
%{_sbindir}/%{name}
%{_libexecdir}/%{name}-launch
%{_libdir}/%{name}/*

%{_datadir}/%{name}/*.glade
%{_datadir}/%{name}/pixmaps/*.png
%{_datadir}/%{name}/pixmaps/*.svg

%{_datadir}/%{name}/*.py
%{_datadir}/%{name}/*.pyc
%{_datadir}/%{name}/*.pyo

%{_datadir}/%{name}/virtManager/*.py
%{_datadir}/%{name}/virtManager/*.pyc
%{_datadir}/%{name}/virtManager/*.pyo

%{_datadir}/%{name}/vncViewer/*.py
%{_datadir}/%{name}/vncViewer/*.pyc
%{_datadir}/%{name}/vncViewer/*.pyo


%{_datadir}/applications/%{name}.desktop
%{_datadir}/dbus-1/services/%{name}.service

%changelog
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
