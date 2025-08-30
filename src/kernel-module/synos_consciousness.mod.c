#include <linux/module.h>
#include <linux/export-internal.h>
#include <linux/compiler.h>

MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};



static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0xb3f7646e, "kthread_should_stop" },
	{ 0xf9a482f9, "msleep" },
	{ 0xcdf00795, "const_pcpu_hot" },
	{ 0x3213f038, "mutex_unlock" },
	{ 0xbb9ed3bf, "mutex_trylock" },
	{ 0xe2d5255a, "strcmp" },
	{ 0x2a8af3ef, "__register_chrdev" },
	{ 0x69b07fa1, "class_create" },
	{ 0xc8cf812f, "device_create" },
	{ 0xcefb0c9f, "__mutex_init" },
	{ 0xf45c3f31, "proc_create" },
	{ 0xa6f223ad, "kthread_create_on_node" },
	{ 0xac4f24ba, "wake_up_process" },
	{ 0x6bc3fbc0, "__unregister_chrdev" },
	{ 0x73ca058d, "class_destroy" },
	{ 0x13c49cc2, "_copy_from_user" },
	{ 0x349cba85, "strchr" },
	{ 0x17518902, "kthread_stop" },
	{ 0x6dbed688, "proc_remove" },
	{ 0x281722e1, "device_destroy" },
	{ 0x9e4f6a2f, "class_unregister" },
	{ 0x902e9281, "seq_read" },
	{ 0xe1c9223, "seq_lseek" },
	{ 0x5427731d, "single_release" },
	{ 0xbdfb6dbb, "__fentry__" },
	{ 0x4bb9d59e, "single_open" },
	{ 0xfcbbf86c, "seq_printf" },
	{ 0x5b8239ca, "__x86_return_thunk" },
	{ 0x656e4a6e, "snprintf" },
	{ 0x88db9f48, "__check_object_size" },
	{ 0x6b10bee1, "_copy_to_user" },
	{ 0x7682ba4e, "__copy_overflow" },
	{ 0xf0fdf6cb, "__stack_chk_fail" },
	{ 0xb43f9365, "ktime_get" },
	{ 0x9166fada, "strncpy" },
	{ 0x75ca79b5, "__fortify_panic" },
	{ 0x122c3a7e, "_printk" },
	{ 0xbf1981cb, "module_layout" },
};

MODULE_INFO(depends, "");


MODULE_INFO(srcversion, "317849E65F5C4792EA07C60");
