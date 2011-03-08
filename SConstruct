import saliweb.build

vars = Variables('config.py')
env = saliweb.build.Environment(vars, ['conf/live.conf'], service_module='multifit_temp')
Help(vars.GenerateHelpText(env))

env.InstallAdminTools()
env.InstallCGIScripts()

Export('env')
SConscript('python/multifit_temp/SConscript')
SConscript('lib/SConscript')
SConscript('txt/SConscript')
SConscript('html/SConscript')
SConscript('test/SConscript')
