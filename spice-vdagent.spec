Name:           spice-vdagent
Version:        0.14.0
Release:        10%{?dist}
Summary:        Agent for Spice guests
Group:          Applications/System
License:        GPLv3+
URL:            http://spice-space.org/
Source0:        http://spice-space.org/download/releases/%{name}-%{version}.tar.bz2
# Fixes from upstream git
Patch1: 0001-vdagent-d-Add-printing-of-version-to-h-output.patch
Patch2: 0002-vdagentd-Advertise-VD_AGENT_CAP_GUEST_LINEEND_LF.patch
Patch3: 0003-buildsys-Build-vdagentd-as-pie-relro-when-possible.patch
Patch4: 0004-Not-having-the-virtio-channel-is-not-an-error-instea.patch
Patch5: 0005-vdagent-x11-Release-clipboard-on-client-disconnect-i.patch
#This patch is in the RHEL6 build but omitted on purpose from the RHEL7
#build, see https://bugzilla.redhat.com/show_bug.cgi?id=1131454#c2 for
#details
#Patch6: 0006-randr-set-physical-screen-size-to-keep-a-constant-96.patch
Patch7: 0007-clipboard-target_to_type-fix-inner-loop-variable-nam.patch
Patch8: 0008-Reply-to-TIMESTAMP-requests.patch
Patch9: 0009-Handle-STRING-selection-type.patch
Patch10: 0010-randr-Make-resolution-changing-more-robust.patch
Patch11: 0011-Don-t-abort-if-XRRSetCrtcConfig-fails.patch
Patch12: 0012-Fix-gdm-autostart-path.patch
Patch13: 0013-data-remove-rsyslog-config-files.patch
Patch14: 0014-vdagent-file-xfers-only-open-the-file-transfer-dir-w.patch
BuildRequires:  systemd-devel glib2-devel spice-protocol >= 0.12.6
BuildRequires:  libpciaccess-devel libXrandr-devel libXinerama-devel
BuildRequires:  libXfixes-devel systemd-units desktop-file-utils libtool
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description
Spice agent for Linux guests offering the following features:

Features:
* Client mouse mode (no need to grab mouse by client, no mouse lag)
  this is handled by the daemon by feeding mouse events into the kernel
  via uinput. This will only work if the active X-session is running a
  spice-vdagent process so that its resolution can be determined.
* Automatic adjustment of the X-session resolution to the client resolution
* Support of copy and paste (text and images) between the active X-session
  and the client


%prep
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
autoreconf -fi


%build
%configure --with-session-info=systemd --with-init-script=systemd
make %{?_smp_mflags} V=2


%install
make install DESTDIR=$RPM_BUILD_ROOT V=2
# rhbz#963201
rm $RPM_BUILD_ROOT%{_sysconfdir}/modules-load.d/spice-vdagentd.conf


%post
%systemd_post spice-vdagentd.service

%preun
%systemd_preun spice-vdagentd.service

%postun
%systemd_postun_with_restart spice-vdagentd.service


%files
%doc COPYING ChangeLog README TODO
/lib/udev/rules.d/70-spice-vdagentd.rules
%{_unitdir}/spice-vdagentd.service
%{_unitdir}/spice-vdagentd.target
%{_prefix}/lib/tmpfiles.d/spice-vdagentd.conf
%{_bindir}/spice-vdagent
%{_sbindir}/spice-vdagentd
%{_var}/run/spice-vdagentd
%{_sysconfdir}/xdg/autostart/spice-vdagent.desktop
# For /usr/share/gdm/autostart/LoginWindow/spice-vdagent.desktop
# We own the dir too, otherwise we must Require gdm
%{_datadir}/gdm
%{_mandir}/man1/%{name}*.1*


%changelog
* Fri Jun 05 2015 Jonathon Jongsma <jjongsma@redhat.com> - 0.14.0-10
- Don't open a separate file manager for each file transfered
  Resolves: rhbz#1168324

* Tue Sep 23 2014 Christophe Fergeau <cfergeau@redhat.com> 0.14.0-9
- Don't install rsyslog config file. This can cause duplicate logging
  to syslog in rhel6->rhel7 upgrades, and is not really useful anyway
  as the same functionality can be achieved with journald
  Resolves: rhbz#1136881

* Tue Aug 19 2014 Christophe Fergeau <cfergeau@redhat.com> 0.14.0-8
- Fix copy and paste issues with vncclient
  Resolves: rhbz#1130218
- Make vdagent more robust against xrandr failures
  Resolves: rhbz#1066422
- Fix autostart of vdagent in gdm
  Resolves: rhbz#1052172

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 0.14.0-7
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 0.14.0-6
- Mass rebuild 2013-12-27

* Tue Sep 10 2013 Hans de Goede <hdegoede@redhat.com> - 0.14.0-5
- Silence session agent error logging when not running in a vm (rhbz#999804)
- Release guest clipboard ownership on client disconnect (rhbz#1003977)

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.14.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul  3 2013 Hans de Goede <hdegoede@redhat.com> - 0.14.0-3
- Advertise clipboard line-endings for copy and paste line-ending conversion
- Build spice-vdagentd as pie + relro

* Mon May 20 2013 Hans de Goede <hdegoede@redhat.com> - 0.14.0-2
- Drop the no longer needed /etc/modules-load.d/spice-vdagentd.conf (#963201)

* Fri Apr 12 2013 Hans de Goede <hdegoede@redhat.com> - 0.14.0-1
- New upstream release 0.14.0
- Adds support for file transfers from client to guest
- Adds manpages for spice-vdagent and spice-vdagentd

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.12.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Jan  8 2013 Hans de Goede <hdegoede@redhat.com> - 0.12.1-1
- New upstream release 0.12.1
- Fixes various issues with dynamic monitor / resolution support

* Mon Nov 12 2012 Hans de Goede <hdegoede@redhat.com> - 0.12.0-2
- Fix setting of mode on non arbitrary resolution capable X driver
- Fix wrong mouse coordinates on vms with multiple qxl devices

* Sat Sep  1 2012 Hans de Goede <hdegoede@redhat.com> - 0.12.0-1
- New upstream release 0.12.0
- This moves the tmpfiles.d to /usr/lib/tmpfiles.d (rhbz#840194)
- This adds a systemd .service file (rhbz#848102)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Mar 27 2012 Hans de Goede <hdegoede@redhat.com> - 0.10.1-1
- New upstream release 0.10.1

* Thu Mar 22 2012 Hans de Goede <hdegoede@redhat.com> - 0.10.0-1
- New upstream release 0.10.0
- This supports using systemd-logind instead of console-kit (rhbz#756398)

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Jul 18 2011 Hans de Goede <hdegoede@redhat.com> 0.8.1-1
- New upstream release 0.8.1

* Fri Jul 15 2011 Hans de Goede <hdegoede@redhat.com> 0.8.0-2
- Make the per session agent process automatically reconnect to the system
  spice-vdagentd when the system daemon gets restarted

* Tue Apr 19 2011 Hans de Goede <hdegoede@redhat.com> 0.8.0-1
- New upstream release 0.8.0

* Mon Mar 07 2011 Hans de Goede <hdegoede@redhat.com> 0.6.3-6
- Fix setting of the guest resolution from a multi monitor client

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 10 2011 Hans de Goede <hdegoede@redhat.com> 0.6.3-4
- Make sysvinit script exit cleanly when not running on a spice enabled vm

* Fri Nov 19 2010 Hans de Goede <hdegoede@redhat.com> 0.6.3-3
- Put the pid and log files into their own subdir (#648553)

* Mon Nov  8 2010 Hans de Goede <hdegoede@redhat.com> 0.6.3-2
- Fix broken multiline description in initscript lsb header (#648549)

* Sat Oct 30 2010 Hans de Goede <hdegoede@redhat.com> 0.6.3-1
- Initial Fedora package
