Summary:	The standard display manager for the X.org X server
Name:		lightdm
Version:	1.9.5
Release:	2
License:	GPL v3
Group:		X11/Applications
Source0:	https://launchpad.net/lightdm/1.9/%{version}/+download/%{name}-%{version}.tar.xz
# Source0-md5:	22f4b8244323ccdaf40667ed964112b9
Source1:	%{name}.service
Source2:	%{name}.tmpfiles
Source3:	%{name}.rules
Source4:	%{name}.pamd
Source5:	%{name}-autologin.pamd
Source6:	%{name}-greeter.pamd
Source10:	Xresources
Source11:	xinitdefs
Source12:	xsession
Patch0:		%{name}-config.patch
URL:		https://launchpad.net/lightdm
BuildRequires:	autoconf
BuildRequires:	dbus-glib-devel
BuildRequires:	docbook-dtd412-xml
BuildRequires:	gettext-devel
BuildRequires:	gobject-introspection-devel
BuildRequires:	gtk-doc
BuildRequires:	intltool
BuildRequires:	libtool
BuildRequires:	libxklavier-devel
BuildRequires:	pam-devel
BuildRequires:	perl-XML-Parser
BuildRequires:	perl-base
BuildRequires:	pkg-config
BuildRequires:	yelp-tools
Requires:	%{name}-libs = %{version}-%{release}
Requires(pre,postun):	pwdutils
Requires(post,preun,postun):	systemd-units
Requires:	lightdm-greeter
Requires:	pam
Requires:	xorg-app-xmodmap
Requires:	xorg-app-xrdb
Requires:	xorg-theme-xcursor-OpenZone
Requires:	xorg-xserver-server
Provides:	group(xdm)
Provides:	user(xdm)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libexecdir	%{_libdir}/lightdm

%description
LightDM is a cross-desktop display manager that aims is to be the
standard display manager for the X.org X server.

%package libs
Summary:	LightDM GObject library
Group:		Libraries

%description libs
LightDM GObject library.

%package devel
Summary:	Header files for lightdm development
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for lightdm development.

%package apidocs
Summary:	lightdm API documentation
Group:		Documentation

%description apidocs
lightdm API documentation.

%prep
%setup -q
%patch0 -p1

# kill gnome common deps
%{__sed} -i -e 's/GNOME_COMPILE_WARNINGS.*//g'	\
    -i -e 's/GNOME_MAINTAINER_MODE_DEFINES//g'	\
    -i -e 's/GNOME_COMMON_INIT//g'		\
    -i -e 's/GNOME_CXX_WARNINGS.*//g'		\
    -i -e 's/GNOME_DEBUG_CHECK//g' configure.ac

%build
%{__libtoolize}
%{__intltoolize}
%{__gtkdocize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-silent-rules		\
	--disable-static		\
	--enable-liblightdm-qt=no	\
	--with-greeter-session=lightdm-gtk-greeter	\
	--with-greeter-user=xdm		\
	--with-html-dir=%{_gtkdocdir}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/var/{cache,log}/lightdm \
	$RPM_BUILD_ROOT%{_datadir}/lightdm/remote-sessions	\
	$RPM_BUILD_ROOT%{_datadir}/lightdm/sessions	\
	$RPM_BUILD_ROOT%{_datadir}/polkit-1/rules.d	\
	$RPM_BUILD_ROOT%{_datadir}/xgreeters	\
	$RPM_BUILD_ROOT%{systemdtmpfilesdir}	\
	$RPM_BUILD_ROOT%{systemdunitdir}	\
	$RPM_BUILD_ROOT/home/services/xdm

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%{__rm} -r $RPM_BUILD_ROOT/etc/{apparmor.d,init}
%{__rm} -r $RPM_BUILD_ROOT%{_localedir}/{lb,wae}

install %{SOURCE1} $RPM_BUILD_ROOT%{systemdunitdir}
install %{SOURCE2} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/lightdm.conf
install %{SOURCE3} $RPM_BUILD_ROOT%{_datadir}/polkit-1/rules.d/lightdm.rules
install %{SOURCE4} $RPM_BUILD_ROOT/etc/pam.d/lightdm
install %{SOURCE5} $RPM_BUILD_ROOT/etc/pam.d/lightdm-autologin
install %{SOURCE6} $RPM_BUILD_ROOT/etc/pam.d/lightdm-greeter

install %{SOURCE10} %{SOURCE11} %{SOURCE12} \
	$RPM_BUILD_ROOT%{_sysconfdir}/lightdm

%find_lang %{name} --with-gnome

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 110 -r -f xdm
%useradd -u 110 -r -d /home/services/xdm -s /usr/bin/false -c "Display Manager" -g xdm xdm

%post
export NORESTART="yes"
%systemd_post lightdm.service
/usr/bin/systemd-tmpfiles --create lightdm.conf >/dev/null 2>&1 || :

%postun
if [ "$1" = "0" ]; then
	%userremove xdm
	%groupremove xdm
fi
%systemd_postun

%post	libs -p /usr/sbin/ldconfig
%postun	libs -p /usr/sbin/ldconfig

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc NEWS
%attr(755,root,root) %{_bindir}/dm-tool
%attr(755,root,root) %{_sbindir}/lightdm

%dir %{_libexecdir}
%attr(755,root,root) %{_libexecdir}/lightdm-guest-session

%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/pam.d/lightdm
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/pam.d/lightdm-autologin
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/pam.d/lightdm-greeter
%attr(750,root,root) /var/log/lightdm
%dir %{_sysconfdir}/lightdm
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lightdm/users.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lightdm/lightdm.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lightdm/keys.conf

%attr(755,root,root) %{_sysconfdir}/lightdm/xsession
%{_sysconfdir}/lightdm/xinitdefs
%{_sysconfdir}/lightdm/Xresources

%{_sysconfdir}/dbus-1/system.d/org.freedesktop.DisplayManager.conf

%dir %attr(710,root,root) /var/cache/lightdm
%dir %attr(710,root,root) /var/log/lightdm
%dir %attr(750,xdm,xdm) /home/services/xdm
%dir %{_datadir}/lightdm
%dir %{_datadir}/lightdm/remote-sessions
%dir %{_datadir}/lightdm/sessions
%dir %{_datadir}/xgreeters

%{_datadir}/polkit-1/rules.d/lightdm.rules
%{systemdtmpfilesdir}/lightdm.conf
%{systemdunitdir}/lightdm.service

%{_mandir}/man1/dm-tool.1.*
%{_mandir}/man1/lightdm*1.*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %ghost %{_libdir}/liblightdm-gobject-1.so.0
%attr(755,root,root) %{_libdir}/liblightdm-gobject-1.so.*.*.*
%{_libdir}/girepository-1.0/LightDM-1.typelib

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/*.so
%{_includedir}/lightdm-gobject-1
%{_pkgconfigdir}/*.pc
%{_datadir}/gir-1.0/*.gir
%{_datadir}/vala/vapi/*.vapi

%files apidocs
%defattr(644,root,root,755)
%{_gtkdocdir}/lightdm-gobject-1

