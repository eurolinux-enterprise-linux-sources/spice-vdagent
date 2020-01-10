Name:           spice-vdagent
Version:        0.14.0
Release:        9%{?dist}
Summary:        Agent for Spice guests
Group:          Applications/System
License:        GPLv3+
URL:            http://spice-space.org/
Source0:        http://spice-space.org/download/releases/%{name}-%{version}.tar.bz2
# For rhbz#799482
Patch1:         0001-vdagentd-Advertise-VD_AGENT_CAP_GUEST_LINEEND_LF.patch
# For rhbz#999804
Patch2:         0002-Not-having-the-virtio-channel-is-not-an-error-instea.patch
# For rhbz#1003977
Patch3:         0003-vdagent-x11-Release-clipboard-on-client-disconnect-i.patch
Patch4:         0004-randr-set-physical-screen-size-to-keep-a-constant-96.patch
# For rhbz#1117764
Patch5:         0005-clipboard-target_to_type-fix-inner-loop-variable-nam.patch
Patch6:         0006-Reply-to-TIMESTAMP-requests.patch
Patch7:         0007-Handle-STRING-selection-type.patch
# For rhbz#1206117, rhbz#1130080 and rhbz#1209550
Patch8:         0008-randr-Make-resolution-changing-more-robust.patch
# For rhbz#1206663
Patch9:         0009-build-sys-Enable-large-file-support.patch
# For rhbz#1086657
Patch10:        0010-randr-remove-monitors.xml-on-auto-configuration.patch
Patch11:        0011-randr-handle-XRRScreenChangeNotifyEvent.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  spice-protocol glib2-devel libpciaccess-devel dbus-devel
BuildRequires:  libXrandr-devel libXinerama-devel libXfixes-devel libtool
BuildRequires:  desktop-file-utils

# For rhbz#120663 -- patch requires autoreconf
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool

ExclusiveArch:  i686 x86_64
Requires:       ConsoleKit
Requires(post):   chkconfig
Requires(postun): initscripts
Requires(preun):  chkconfig
Requires(preun):  initscripts

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
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
autoreconf --install --force
cp -a data/rsyslog.d/spice-vdagentd.conf rsyslog.conf


%build
export CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"
%configure
make V=2 %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make V=2 install DESTDIR=$RPM_BUILD_ROOT
# RHEL-6 has no /etc/rsyslog.d
rm $RPM_BUILD_ROOT%{_sysconfdir}/rsyslog.d/spice-vdagentd.conf


%clean
rm -rf $RPM_BUILD_ROOT


%post
/sbin/chkconfig --add spice-vdagentd
if ! grep -q spice-vdagent /etc/rsyslog.conf; then
  echo >> /etc/rsyslog.conf
  cat %{_datadir}/doc/%{name}-%{version}/rsyslog.conf >> /etc/rsyslog.conf
fi

%preun
if [ $1 = 0 ] ; then
    /sbin/service spice-vdagentd stop >/dev/null 2>&1
    /sbin/chkconfig --del spice-vdagentd
fi

%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service spice-vdagentd condrestart >/dev/null 2>&1 || :
fi


%files
%defattr(-,root,root,-)
%doc COPYING ChangeLog README TODO rsyslog.conf
%{_initddir}/spice-vdagentd
%{_bindir}/spice-vdagent
%{_sbindir}/spice-vdagentd
%{_var}/run/spice-vdagentd
%{_sysconfdir}/xdg/autostart/spice-vdagent.desktop
# For /usr/share/gdm/autostart/LoginWindow/spice-vdagent.desktop
# We own the dir too, otherwise we must Require gdm
%{_datadir}/gdm
%{_mandir}/man1/spice-vdagent*.1*


%changelog
* Fri Apr 10 2015 Fabiano Fidêncio <fidencio@redhat.com> 0.14.0-9
- Add -fno-strict-aliasing to CFLAGS
  Related: rhbz#1086657

* Fri Apr 10 2015 Fabiano Fidêncio <fidencio@redhat.com> 0.14.0-8
- Cannot get same result enablng second monitor after it was disabled using
  Guest's "Display Preference"
  Resolves: rhbz#1086657

* Fri Apr 10 2015 Fabiano Fidêncio <fidencio@redhat.com> 0.14.0-7
- build-sys: Enable large file support
  Resolves: rhbz#1206663

* Tue Apr 07 2015 Fabiano Fidêncio <fidencio@redhat.com> 0.14.0-6
- randr: Make resolution changing more robust
  Resolves: rhbz#1206117, rhbz#1130080 and rhbz#1209550

* Mon Mar 02 2015 Christophe Fergeau <cfergeau@redhat.com> 0.14.0-5
- Add support for TIMESTAMP/STRING selection types, this fixes copy and paste
  issues with some applications (vncviewer for example).
  Resolves: rhbz#1117764

* Tue Jul 22 2014 Marc-Andre Lureau <mlureau@redhat.com> - 0.14.0-4
- Rebuild for update to work against z-stream.
  Resolves: rhbz#1066094

* Fri Mar 14 2014 Marc-Andre Lureau <mlureau@redhat.com> - 0.14.0-3
- set physical screen size to keep a constant 96 dpi
  Resolves: rhbz#1066094

* Tue Sep 10 2013 Hans de Goede <hdegoede@redhat.com> - 0.14.0-2
- Silence session agent error logging when not running in a vm
  Resolves: rhbz#999804
- Release guest clipboard ownership on client disconnect
  Resolves: rhbz#1003977

* Mon Jun 24 2013 Hans de Goede <hdegoede@redhat.com> - 0.14.0-1
- Rebase to spice-vdagent-0.14.0 release
- Drop all patches (all upstream)
  Resolves: rhbz#951596
- Advertise Unix line-endings for clipboard data
  Resolves: rhbz#799482
- Add support for setups with multiple Screens
  Resolves: rhbz#904082
- Make console-kit integration runtime configurable
  Resolves: rhbz#904084

* Sat Mar  9 2013 Hans de Goede <hdegoede@redhat.com> - 0.12.0-5
- Allow having a sparse monitor config (ie monitor 1 and 3 active)
  Resolves: rhbz#894036
- Fix session spice-vdagent crash on system spice-vdagentd restart
  Resolves: rhbz#894365
- Don't log a warning when there are less qxl devices then monitors
  Resolves: rhbz#895004
- Restore old monitor config when failing to set a new monitor config
  Resolves: rhbz#881020

* Tue Jan  8 2013 Hans de Goede <hdegoede@redhat.com> - 0.12.0-4
- Fix various issues with dynamic resolution and monitor support
  Resolves: rhbz#888821

* Mon Nov 26 2012 Marc-André Lureau <marcandre.lureau@redhat.com> - 0.12.0-3
- Fix crash when first resizing monitor
  Resolves: rhbz#872633

* Sun Oct 14 2012 Hans de Goede <hdegoede@redhat.com> - 0.12.0-2
- Fix wrong mouse coordinates on vms with multiple qxl devices
  Resolves: rhbz#855110

* Sat Sep  1 2012 Hans de Goede <hdegoede@redhat.com> - 0.12.0-1
- New upstream release 0.12.0
  Resolves: rhbz#842355
- This switches to syslog for logging, adding timestamps, etc. to the logs
  Resolves: rhbz#747894
- This adds support for dynamically adding monitors and resolutions
  Resolves: rhbz#842298

* Fri Oct 28 2011 Hans de Goede <hdegoede@redhat.com> 0.8.1-3
- Fix resolution sync not working when connecting with a multi monitor client
  to a single monitor guest
  Resolves: rhbz#748760

* Mon Oct  3 2011 Hans de Goede <hdegoede@redhat.com> 0.8.1-2
- Add support for multiple monitors / Xinerama setups
  Resolves: rhbz#740851

* Mon Jul 18 2011 Hans de Goede <hdegoede@redhat.com> 0.8.1-1
- New upstream release 0.8.1
  Resolves: rhbz#722477
- Fixes vdagent not auto restarting when vdagentd gets restarted
  Resolves: rhbz#681797
- Fixes vdagent crash when copying large (multiple megabytes) amount of data
  from the client clipboard to the guest clipboard
  Resolves: rhbz#690164

* Thu Mar 24 2011 Hans de Goede <hdegoede@redhat.com> 0.6.3-8
- Fix chunk demultiplexing when chunks from messages for different ports
  get intermixed
  Related: rhbz#658464

* Thu Mar 17 2011 Hans de Goede <hdegoede@redhat.com> 0.6.3-7
- Daemonize per user session vdagent process on startup, this avoids a long
  delay after logging in
- Fix mouse not working with the agent installed
  Resolves: rhbz#688257

* Mon Mar 07 2011 Hans de Goede <hdegoede@redhat.com> 0.6.3-6
- Fix setting of the guest resolution from a multi monitor client
  Resolves: rhbz#680227
- Limit build archs to i686 and x86_64
  Related: rhbz#658464

* Mon Jan 10 2011 Hans de Goede <hdegoede@redhat.com> 0.6.3-5
- Make sysvinit script exit cleanly when not running on a spice enabled vm
  Related: rhbz#658464

* Tue Dec 14 2010 Hans de Goede <hdegoede@redhat.com> 0.6.3-4
- Build for RHEL-6
  Resolves: rhbz#658464

* Fri Nov 19 2010 Hans de Goede <hdegoede@redhat.com> 0.6.3-3
- Put the pid and log files into their own subdir (#648553)

* Mon Nov  8 2010 Hans de Goede <hdegoede@redhat.com> 0.6.3-2
- Fix broken multiline description in initscript lsb header (#648549)

* Sat Oct 30 2010 Hans de Goede <hdegoede@redhat.com> 0.6.3-1
- Initial Fedora package
