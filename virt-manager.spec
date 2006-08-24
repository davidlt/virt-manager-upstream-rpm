# -*- rpm-spec -*-

# This macro is used for the continuous automated builds. It just
# allows an extra fragment based on the timestamp to be appended
# to the release. This distinguishes automated builds, from formal
# Fedora RPM builds
%define _extra_release %{?extra_release:%{extra_release}}

Name: virt-manager
Version: 0.2.0
Release: 1%{_extra_release}
Summary: Virtual Machine Manager

Group: Applications/Emulators
License: GPL
URL: http://virt-manager.et.redhat.com/
Source0: http://virt-manager.et.redhat.com/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# These two are just the oldest version tested
Requires: pygtk2 >= 1.99.12-6
Requires: gnome-python2-gconf >= 1.99.11-7
# Absolutely require this version or newer
Requires: libvirt-python >= 0.1.4-3
# Definitely does not work with earlier due to python API changes
Requires: dbus-python >= 0.61
# Might work with earlier, but this is what we've tested
# We use 'ctypes' so don't need the 'gnome-keyring-python' bits
Requires: gnome-keyring >= 0.4.9
# Minimum we've tested with
# Although if you don't have this, comment it out and the app
# will work just fine - keyring functionality will simply be
# disabled 
Requires: gnome-python2-gnomekeyring >= 2.15.4
# Minimum we've tested with
Requires: libxml2-python >= 2.6.23
# Required to install Xen guests
Requires: python-xeninst >= 0.90.1

# Earlier vte han broken python binding module
Requires: vte >= 0.12.2

BuildRequires: pygtk2-devel
BuildRequires: gtk2-devel
BuildRequires: python-devel

%description
Virtual Machine Manager provides a graphical tool for administering
virtual machines such as Xen. It uses libvirt as the backend management
API.

%prep
%setup -q

%build
%configure
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install  DESTDIR=$RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}/sparkline.a
rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}/sparkline.la
%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc README COPYING AUTHORS ChangeLog NEWS
%{_bindir}/%{name}
%{_libexecdir}/%{name}-launch
%{_libdir}/%{name}/*

%{_datadir}/%{name}/*.glade
%{_datadir}/%{name}/pixmaps/*.png
%{_datadir}/%{name}/pixmaps/*.svg

%{_datadir}/%{name}/*.py
%{_datadir}/%{name}/*.pyc
%ghost %{_datadir}/%{name}/*.pyo

%{_datadir}/%{name}/virtManager/*.py
%{_datadir}/%{name}/virtManager/*.pyc
%ghost %{_datadir}/%{name}/virtManager/*.pyo

%{_datadir}/%{name}/vncViewer/*.py
%{_datadir}/%{name}/vncViewer/*.pyc
%ghost %{_datadir}/%{name}/vncViewer/*.pyo


%{_datadir}/applications/%{name}.desktop
%{_datadir}/dbus-1/services/%{name}.service

%changelog
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
