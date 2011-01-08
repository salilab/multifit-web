package multifit;
use base qw(saliweb::frontend);
use strict;

sub new {
    return saliweb::frontend::new(@_, @CONFIG@);
}

sub get_navigation_links {
    my $self = shift;
    my $q = $self->cgi;
    return [
        $q->a({-href=>$self->index_url}, "Multifit Home"),
        $q->a({-href=>$self->queue_url}, "Current Queue"),
        $q->a({-href=>$self->help_url}, "Help"),
        #$q->a({-href=>$self->faq_url}, "FAQ"),
        $q->a({-href=>$self->contact_url}, "Contact")
        ];
}

sub get_project_menu {
    # TODO
    my $self = shift;
    return <<MENU;
MENU
}

sub get_footer {
    my $self = shift;
    my $htmlroot = $self->htmlroot;
    return <<FOOTER;
<div id="address">
<center><a target="_blank" href="http://www.ncbi.nlm.nih.gov/pubmed/20827723">
<b>K. Lasker,  M. Topf, A. Sali and H. Wolfson, Journal of Molecular Biology, (2009) <i>388,</i> 180-194</b></a>
&nbsp;<a href="http://salilab.org/pdf/Lasker_Proteins-StructFunctBioinform_2010a.pdf"><img src="$htmlroot/img/pdf.gif" alt="PDF" /></a><br />
</div>
FOOTER
}

sub get_index_page {
    # TODO
    my $self = shift;
    my $q = $self->cgi;
    my $symmetryModeValues = ['symmetric', 'non_symmetric'];
    my $symmetryModeLabels;
    $symmetryModeLabels->{"symmetric"} = "Symmetric Mode";
    $symmetryModeLabels->{"non_symmetric"} = "Non-Symmetric Mode";
    my $greeting = <<GREETING;
<p>Multifit is a computational method for simultaneously fitting atomic structures
of components into their assembly density map at resolutions as low as 25 A.
The component positions and orientations are optimized with respect to a scoring
function that includes the quality-of-fit of components in the map, the protrusion
of components from the map envelope, as well as the shape complementarity between
pairs of components.
The scoring function is optimized by an exact inference optimizer DOMINO that
efficiently finds the global minimum in a discrete sampling space.
<br />&nbsp;</p>
GREETING
    return "<div id=\"resulttable\">\n" .
           $q->h2({-align=>"center"},
                  "Multifit: Fitting of multiple proteins into their assembly density map") .
           $q->start_form({-name=>"multifit_form", -method=>"post",
                           -action=>$self->submit_url}) .
           $q->table(
               $q->Tr($q->td({-colspan=>2}, $greeting)) .
               $q->Tr($q->td($q->h4("General information"
                                    ))) .
               $q->Tr($q->td("Email address"),
                      $q->td($q->textfield({-name=>"email",
                                            -value=>$self->email,
                                            -size=>"25"}))) .
               $q->Tr($q->td("Name your job"),
                      $q->td($q->textfield({-name=>"name",
                                            -size=>"25"}))) .
               $q->Tr($q->td($q->h4("Complex information")),
		      ) .
               $q->Tr($q->td("Select symmetry mode",
                             $self->help_link("symmetry_mode")),
                      $q->td($q->radio_group("symmetry_mode", $symmetryModeValues, 
                                             "symmetric", 0, $symmetryModeLabels))) .
               $q->Tr($q->td("Number of Cn Symmetry",
                             $self->help_link("cn_symmetry")),
                      $q->td($q->textfield({-name=>"cn_symmetry",
                                            -size=>"25"}))) .
               $q->Tr($q->td($q->h4("Complex EM density map information"
                                    ))) .
               $q->Tr($q->td("Upload EM density map",
                             $self->help_link("map"), $q->br),
                      $q->td($q->filefield({-name=>"map"}))) .
               $q->Tr($q->td("Resolution",
                             $self->help_link("resolution")),
                      $q->td($q->textfield({-name=>"resolution",
                                            -size=>"25"}))) .
               $q->Tr($q->td("Spacing",
                             $self->help_link("spacing")),
                      $q->td($q->textfield({-name=>"spacing",
                                            -size=>"25"}))) .
               $q->Tr($q->td("Density threshold",
                             $self->help_link("density_threshold")),
                      $q->td($q->textfield({-name=>"density_threshold",
                                            -size=>"25"}))) .
               $q->Tr($q->td($q->h4("Subunits information",
                                    ))) .
               $q->Tr($q->td("subunit pdb coordinate file",
                             $self->help_link("file"), $q->br),
                      $q->td($q->filefield({-name=>"pdb"}))) .
               #$q->Tr($q->td($q->h4("Advanced options",
                             #       $self->help_link("advanced_option")))) .
                             #       #$self->help_link("advanced_option"))),
			     #$q->td($q->a({-href=>"$search_url?".&get_linkoptions(
                             #             "advanced_properties","y")}, "Show"),
			     #       $q->a({-href=>"$search_url?".&get_linkoptions(
                             #             "advanced_properties","n")}, "Hide"))) .
               $q->Tr($q->td({-colspan=>"2"},
                             "<center>" .
                             $q->input({-type=>"submit", -value=>"Process"}) .
                             $q->input({-type=>"reset", -value=>"Reset"}) .
                             "</center><p>&nbsp;</p>"))) .
           $q->end_form .
           "</div>\n";
}

sub get_submit_page {
    # TODO
    my $self = shift;
    my $q = $self->cgi;

    my $input_pdb = $q->upload('pdb');                  # uploaded file handle
    my $input_map = $q->upload('map')||"";              # user-provided density map 
    my $user_name = $q->param('name')||"";              # user-provided job name
    my $email     = $q->param('email')||"";          # user's e-mail
    my $resolution= $q->param('resolution')||"";        # user-provided resolution 
    my $spacing   = $q->param('spacing')||"";           # user-provided spacing 
    my $symmetry_mode = $q->param('symmetry_mode')||""; # user-provided symmetry mode 
    my $cn_symmetry = $q->param('cn_symmetry')||"";     # user-provided number of Cn symmetry 
    my $density_threshold = $q->param('density_threshold')||""; # user-provided density threshold 

    # Validate input
    my $file_contents = "";
    my $map_contents = "";
    my $atoms = 0;
    while (<$input_pdb>) {
        if (/^ATOM  /) { $atoms++; }
        $file_contents .= $_;
    }
    if ($atoms == 0) {
        throw saliweb::frontend::InputValidationError(
                   "PDB file contains no ATOM records!");
    }
    while (<$input_map>) {
        $map_contents .= $_;
    }
    if ($email eq "") {
        throw saliweb::frontend::InputValidationError(
                   "Email is missing!");
    }
    if ($user_name eq "") {
        throw saliweb::frontend::InputValidationError(
                   "Job name is missing!");
    }
    if ($resolution eq "") {
        throw saliweb::frontend::InputValidationError(
                   "Resolution input is missing!");
    }
    if ($spacing eq "") {
        throw saliweb::frontend::InputValidationError(
                   "Spacing input is missing!");
    }
    if ($symmetry_mode eq "non_symmetric") {
        throw saliweb::frontend::InputValidationError(
                   "Non symmetric mode is currently no supported!");
    }
    # Create job directory, add input files, then submit the job
    my $job = $self->make_job($user_name);
    my $jobdir = $job->directory;

    $input_pdb = $jobdir . "/input.pdb";
    open(INPDB, "> $input_pdb")
       or throw saliweb::frontend::InternalError("Cannot open $input_pdb: $!");
    print INPDB $file_contents;
    close INPDB
       or throw saliweb::frontend::InternalError("Cannot close $input_pdb: $!");

    $input_map = $jobdir . "/input.map";
    open(INMAP, "> $input_map")
       or throw saliweb::frontend::InternalError("Cannot open $input_map: $!");
    print INMAP $map_contents;
    close INMAP
       or throw saliweb::frontend::InternalError("Cannot close $input_map: $!");

    my $input_param = $jobdir . "/param.txt";
    open(INPARAM, "> $input_param")
       or throw saliweb::frontend::InternalError("Cannot open $input_param: $!");
    print INPARAM "$resolution\n";
    print INPARAM "$spacing\n";
    print INPARAM "$density_threshold\n";
    print INPARAM "$cn_symmetry\n";

    close INPARAM
       or throw saliweb::frontend::InternalError("Cannot close $input_param: $!");

    $job->submit($email);


    # Inform the user of the job name and results URL
    my $return=
      $q->h1("Job Submitted") .
      $q->hr .
      $q->p("Your job " . $job->name . " has been submitted to the server.");
    if ($email) {
        $return.=$q->p("<BR>You will be notified at $email when <a href=\"" .
            $job->results_url . "\">job results</a> " . "are available.");
    }

    $return .=
      $q->p("<BR>You can check on your job at the " .
            "<a href=\"" . $self->queue_url .
            "\">Multifit current queue page</a>.").
      #$q->p("The estimated execution time is ~90 min, depending on the load.").
      $q->p("<BR>If you experience any problems or if you do not receive the results " .
            "for more than 12 hours, please <a href=\"" .
            $self->contact_url . "\">contact us</a>.") .
      $q->p("<BR>Thank you for using our server and good luck in your research!");

    return $return;
}

sub get_results_page {
    my ($self, $job) = @_;
    my $q = $self->cgi;

    if (-f "multifit.output"){
        return $self->display_ok_job($q, $job);
    } else{
        return $self->display_failed_job($q, $job);
    }
}

sub trim($) {
   my $string = shift;
   $string =~ s/^\s+//;
   $string =~ s/\s+$//;
   return $string;
}

sub read_multifit_output_file {
   open(MULT_OUT, "< multifit.output") or die "Can't open multifit.output: $!";

   my %fit_solution;
   my @header_array = map (trim($_), split (/\|/, <MULT_OUT>));
   while(<MULT_OUT>){
      my @line_array = split (/\|/, $_);
      my $i = 0;
	    foreach my $header (@header_array){
   	    push @{ $fit_solution{$header} }, $line_array[$i++];
	    }
   }
   close MULT_OUT or die "Can't close multifit.output: $!";

   return %fit_solution;
}

sub display_ok_job {
   my ($self, $q, $job) = @_;
   my $return= $q->p("Job '<b>" . $job->name . "</b>' has completed.");

   my %fit_solution = read_multifit_output_file();
   my $total_solution = scalar @{$fit_solution{"solution index"}};

   my $contents = "";
   for ( my $j=0; $j < $total_solution-1; $j++ )
   {
      $contents .= $q->Tr($q->td($j),#$fit_solution{"solution index"}[$j]), 
                   $q->td("<a href=\"" . 
           $job->get_results_file_url($fit_solution{"solution filename"}[$j]) . 
           "\">" . $fit_solution{"solution filename"}[$j] . "</a>"),
                   $q->td(1-$fit_solution{"cluster size"}[$j])); 
   }
   $return.= $q->p(
             $q->table(
             $q->Tr($q->td("Solution Index") .
                    $q->td("PDB Model") .
                    $q->td("Cross Correlation Score")) . 
             $contents));
 
   $return.= $q->p("<BR><a href=\"" . 
          $job->get_results_file_url("multifit.output") .
          "\">Download multifit.output file</a>.");

   $return .= $job->get_results_available_time();

   return $return;
}

sub display_failed_job {
    my ($self, $q, $job) = @_;
    my $return= $q->p("Your Multifit job '<b>" . $job->name .
                      "</b>' failed to produce any output models.");
    $return.=$q->p("This is usually caused by incorrect inputs " .
                   "(e.g. corrupt PDB file).");
    $return.=$q->p("For a discussion of some common input errors, please see " .
                   "the " .
                   $q->a({-href=>$self->help_url . "#errors"}, "help page") .
                   ".");
    $return.= $q->p("For more information, you can " .
                    "<a href=\"" . $job->get_results_file_url("failure.log") .
                    "\">download the Multifit log file</a>." .
                    "<BR>If the problem is not clear from this log, " .
                    "please <a href=\"" .
                    $self->contact_url . "\">contact us</a> for " .
                    "further assistance.");
    return $return;
}

1;
