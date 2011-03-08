use saliweb::Test;
use Test::More 'no_plan';
use Test::Exception;
use File::Temp qw(tempdir);

BEGIN {
    use_ok('multifit_temp');
    use_ok('saliweb::frontend');
}

my $t = new saliweb::Test('multifit_temp');

# Test get_navigation_links
{
    my $frontend = $t->make_frontend();
    my $links = $frontend->get_navigation_links();
    isa_ok($links, 'ARRAY', 'navigation links');
    like($links->[0], qr#<a href="http://modbase/top/">Multifit Temp Home</a>#,
         'Index link');
    like($links->[1], qr#<a href="http://modbase/top/queue.cgi">Current Queue</a>#,
         'Queue link');
    like($links->[2], qr#<a href="http://modbase/top/help.cgi\?type=help">Help</a>#,
         'Help link');
    like($links->[3], qr#<a href="http://modbase/top/help.cgi\?type=contact">Contact</a>#,
         'Contact link');
}

# Check results page

# Test allow_file_download
{
    my $self = $t->make_frontend();
    is($self->allow_file_download('bad.log'), '',
       "allow_file_download bad file");
    is($self->allow_file_download('multifit.output'), 1,
       "                    good file");
    is($self->allow_file_download('asmb.model.9.pdb'), 1,
       "                    good file");
    is($self->allow_file_download('asmb.models.tar.gz'), 1,
       "                    good file");
    is($self->allow_file_download('asmb.model.5.jpg'), 1,
       "                    good file");
}

# Check display_ok_job
{
    my $frontend = $t->make_frontend();
    my $job = new saliweb::frontend::CompletedJob($frontend,
                        {name=>'testjob', passwd=>'foo', directory=>'/foo/bar',
                         archive_time=>'2011-01-01 08:45:00'});
    my $ret = $frontend->display_ok_job($frontend->{CGI}, $job);
    like($ret, '/Job.*testjob.*has completed.*/ms', 'display_ok_job');
}

# Check display_failed_job
{
    my $frontend = $t->make_frontend();
    my $job = new saliweb::frontend::CompletedJob($frontend,
                        {name=>'testjob', passwd=>'foo', directory=>'/foo/bar',
                         archive_time=>'2009-01-01 08:45:00'});
    my $ret = $frontend->display_failed_job($frontend->{CGI}, $job);
    like($ret, '/Your Multifit job.*testjob.*failed to produce any output models.*' .
               'please see the.*#errors.*help page.*For more information, ' .
               'you can.*failure\.log.*download the Multifit log file.*' .
               'contact us/ms', 'display_failed_job');
}

# Check get_results_page
{
    my $frontend = $t->make_frontend();
    my $job = new saliweb::frontend::CompletedJob($frontend,
                        {name=>'testjob', passwd=>'foo', directory=>'/foo/bar',
                         archive_time=>'2009-01-01 08:45:00'});
    my $tmpdir = tempdir(CLEANUP=>1);
    ok(chdir($tmpdir), "chdir into tempdir");

    my $ret = $frontend->get_results_page($job);
    like($ret, '/Your Multifit job.*testjob.*failed to produce any output models./',
         'get_results_page (failed job)');

    ok(open(FH, "> multifit.output"), "Open multifit.output");
    ok(close(FH), "Close multifit.output");

    $ret = $frontend->get_results_page($job);
    like($ret, '/Job.*testjob.*has completed/',
         '                 (successful job)');

    chdir("/");
}
