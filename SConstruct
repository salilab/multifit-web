import saliweb.build

vars = Variables('config.py')
env = saliweb.build.Environment(vars, ['conf/live.conf'], service_module='multifit')
Help(vars.GenerateHelpText(env))

env.InstallAdminTools()

Export('env')
SConscript('backend/multifit/SConscript')
SConscript('frontend/multifit/SConscript')
SConscript('html/SConscript')
SConscript('test/SConscript')
