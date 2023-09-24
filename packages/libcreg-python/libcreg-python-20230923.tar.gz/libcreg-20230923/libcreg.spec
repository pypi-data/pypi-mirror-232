Name: libcreg
Version: 20230923
Release: 1
Summary: Library to access the Windows 9x/Me Registry File (CREG) format
Group: System Environment/Libraries
License: LGPL-3.0-or-later
Source: %{name}-%{version}.tar.gz
URL: https://github.com/libyal/libcreg
            
BuildRequires: gcc            

%description -n libcreg
Library to access the Windows 9x/Me Registry File (CREG) format

%package -n libcreg-static
Summary: Library to access the Windows 9x/Me Registry File (CREG) format
Group: Development/Libraries
Requires: libcreg = %{version}-%{release}

%description -n libcreg-static
Static library version of libcreg.

%package -n libcreg-devel
Summary: Header files and libraries for developing applications for libcreg
Group: Development/Libraries
Requires: libcreg = %{version}-%{release}

%description -n libcreg-devel
Header files and libraries for developing applications for libcreg.

%package -n libcreg-python3
Summary: Python 3 bindings for libcreg
Group: System Environment/Libraries
Requires: libcreg = %{version}-%{release} python3
BuildRequires: python3-devel

%description -n libcreg-python3
Python 3 bindings for libcreg

%package -n libcreg-tools
Summary: Several tools for reading Windows 9x/Me Registry Files (CREG)
Group: Applications/System
Requires: libcreg = %{version}-%{release} fuse-libs
BuildRequires: fuse-devel

%description -n libcreg-tools
Several tools for reading Windows 9x/Me Registry Files (CREG)

%prep
%setup -q

%build
%configure --prefix=/usr --libdir=%{_libdir} --mandir=%{_mandir} --enable-python3
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
%make_install

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files -n libcreg
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.so.*

%files -n libcreg-static
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.a

%files -n libcreg-devel
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.so
%{_libdir}/pkgconfig/libcreg.pc
%{_includedir}/*
%{_mandir}/man3/*

%files -n libcreg-python3
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/python3*/site-packages/*.a
%{_libdir}/python3*/site-packages/*.so

%files -n libcreg-tools
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_bindir}/*
%{_mandir}/man1/*

%changelog
* Sun Sep 24 2023 Joachim Metz <joachim.metz@gmail.com> 20230923-1
- Auto-generated

