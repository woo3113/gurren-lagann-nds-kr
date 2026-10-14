export EMU=$HOME/emu
export LD_LIBRARY_PATH=$EMU/squashfs-root/usr/lib:$EMU/libs/usr/lib/x86_64-linux-gnu
export LIBGL_DRIVERS_PATH=$EMU/libs/usr/lib/x86_64-linux-gnu/dri
export __EGL_VENDOR_LIBRARY_DIRS=$EMU/libs/usr/share/glvnd/egl_vendor.d
export QT_QPA_PLATFORM=xcb LIBGL_ALWAYS_SOFTWARE=1
export QT_PLUGIN_PATH=$EMU/squashfs-root/usr/plugins
