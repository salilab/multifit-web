package multifit;
use saliweb::frontend;
use strict;
use Error qw(:try);
use Scalar::Util qw(looks_like_number);

our @ISA = "saliweb::frontend";

sub new {
    return saliweb::frontend::new(@_, "##CONFIG##");
}

# Add our own CSS and JS to the page header
sub get_start_html_parameters {
    my ($self, $style) = @_;
    my %param = $self->SUPER::get_start_html_parameters($style);
    push @{$param{-style}->{'-src'}}, $self->htmlroot . 'js/tab.css';
    push @{$param{-script}}, {-language => 'JavaScript',
                              -src=> $self->htmlroot . "js/tab.js"};
    return %param;
}

sub get_navigation_links {
    my $self = shift;
    my $q = $self->cgi;
    return [
        $q->a({-href=>$self->index_url}, "MultiFit Home"),
        $q->a({-href=>$self->queue_url}, "Current Queue"),
        $q->a({-href=>$self->help_url}, "Help"),
        $q->a({-href=>$self->contact_url}, "Contact")
        #$q->a({-href=>$self->faq_url}, "FAQ"),
        ];
}

sub get_project_menu {
    my $self = shift;
    return <<MENU;
<p>&nbsp;</p>
MENU
}

sub get_footer {
    my $self = shift;
    my $htmlroot = $self->htmlroot;
    return <<FOOTER;
<div id="address">
<center>
<hr />
<table>
<tr> <td align="center">
<a target="_blank" rel="noopener noreferrer" href="http://bioinfo3d.cs.tau.ac.il/"><img height="25" src="$htmlroot/img/BioInfo3Dsmall.png" alt="BioInfo3D" /></a>
</td><td>
<a target="_blank" rel="noopener noreferrer" href="http://bioinfo3d.cs.tau.ac.il/">
<b>BioInfo3D</b></a> Servers for protein structure analysis and modeling.
</td>
</tr>
<tr><td align="center">
<a target="_blank" rel="noopener noreferrer" href="http://www.emdatabank.org/"><img height="25" src="$htmlroot/img/EMDBsml.gif" alt="EMDB" /></a>&nbsp;
</td><td>
<a target="_blank" rel="noopener noreferrer" href="http://www.emdatabank.org/"><b>EMDB</b></a> Database for electron microscopy density maps.
</td></tr>
</table>
<hr />
<br />
<a target="_blank" rel="noopener noreferrer" href="https://pubmed.ncbi.nlm.nih.gov/21715383">
<b>E. Tjioe,  K. Lasker, B. Webb, H. Wolfson and A. Sali, Nucleic Acids Research, (2011) <i>39,</i> W167-W170</b></a>
&nbsp;<a target="_blank" rel="noopener noreferrer" href="https://salilab.org/pdf/Tjioe_NucleicAcidsRes_2011.pdf"><img src="$htmlroot/img/pdf.gif" alt="PDF" /></a><br />
<br />
<a target="_blank" rel="noopener noreferrer" href="https://pubmed.ncbi.nlm.nih.gov/20827723">
<b>K. Lasker,  M. Topf, A. Sali and H. Wolfson, Journal of Molecular Biology, (2009) <i>388,</i> 180-194</b></a>
&nbsp;<a target="_blank" rel="noopener noreferrer" href="https://salilab.org/pdf/Lasker_Proteins-StructFunctBioinform_2010a.pdf"><img src="$htmlroot/img/pdf.gif" alt="PDF" /></a><br />
</center>
</div>
FOOTER
}

sub get_index_page {
    my $self = shift;
    my $q = $self->cgi;
    my $greeting = <<GREETING;
<p>MultiFit is a computational method for simultaneously fitting atomic structures
of components into their assembly density map at resolutions as low as 25 &#8491;.
The component positions and orientations are optimized with respect to a scoring
function that includes the quality-of-fit of components in the map, the protrusion
of components from the map envelope, as well as the shape complementarity between
pairs of components.
The scoring function is optimized by an exact inference optimizer DOMINO that
efficiently finds the global minimum in a discrete sampling space.
<br />&nbsp;</p>
GREETING
#You can also <a href="download.cgi">download the
#MultiFit software</a> to run calculations on your own computer.
#<br />&nbsp;</p>
    return "<div id=\"resulttable\">\n" .
           $q->h2({-align=>"left"},
                  "MultiFit: Fitting of multiple proteins into their assembly density map") .
           $q->start_form({-name=>"multifit_form", -method=>"post",
                           -action=>$self->submit_url}) .
           $q->table(
               $q->Tr($q->td({-colspan=>2}, $greeting)) .
               $self->get_general_information_input() .
               $self->get_map_information_input() .
               $self->get_optional_option() .
               $self->get_complex_information_input() 
           ) . 
           $q->table(
               $q->Tr($q->td({-colspan=>"2"},
                      $q->input({-type=>"submit", -value=>"Process job"}) .
                      $q->input({-type=>"reset", -value=>"Reset all values"}) .
                             "<p>&nbsp;</p>"))) .
           $q->end_form .
           "</div>\n";
}

sub get_complex_information_input {
    my $self = shift;
    my $q = $self->cgi;
    return
       $q->Tr($q->td($q->h4("Complex information"))) .
       $q->Tr($q->td("Select symmetry mode",
                     $self->help_link("symmetry_mode"))) .

       $q->Tr($q->td({-colspan=>"3"}, $q->div({-class=>'tabber'},
                         $q->div({-class=>'tabbertab'},
                             $q->h2("Cyclic Symmetry Mode"),
                             $q->table($self->get_symmetry_mode())) .
                         $q->div({-class=>'tabbertab'},
                             $q->h2("Non-Symmetry Mode"),
                             $q->table($self->get_non_symmetry_mode(4, 0))) 
                      )));
}

sub get_symmetry_mode {
    my $self = shift;
    my $q = $self->cgi;
    return
        $q->Tr($q->td("Subunit pdb coordinate file",
                       $self->help_link("file"), $q->br),
               $q->td($q->filefield({-name=>"symm_pdb"}))) .
        $q->Tr($q->td("Symmetry order",
                   $self->help_link("cn_symmetry")),
               $q->td( $q->textfield({-name=>"cn_symmetry",
                                      -size=>"25"}))) 
}

sub get_non_symmetry_mode {
    my ($self, $print_subunit, $start_value) = @_;
    my $q = $self->cgi;
    my $contents = "";

    
    $contents .= $q->Tr($q->td("Non-symmetry mode is not currently available through this web service. There is, however, an equivalent <a href=\"https://integrativemodeling.org/2.4.0/doc/tutorial/multifit_3sfd.html\">command line tool</a> available as part of the <a href=\"https://integrativemodeling.org/\">IMP software</a>."));
    return $contents;
}

sub get_map_information_input {
    my $self = shift;
    my $q = $self->cgi;
    return
              $q->Tr($q->td($q->h4("Complex EM density map information"))) .
              $q->Tr($q->td("Upload EM density map",
                             $self->help_link("map"), $q->br),
                     $q->td($q->filefield({-name=>"map"}))) .
              $q->Tr($q->td("Resolution",
                             $self->help_link("resolution")),
                     $q->td($q->textfield({-name=>"resolution",
                                           -size=>"25"}))) .
              $q->Tr($q->td("Voxel spacing",
                             $self->help_link("spacing")),
                     $q->td($q->textfield({-name=>"spacing",
                                           -size=>"25"}))) .
              $q->Tr($q->td("Contour level",
                             $self->help_link("threshold")),
                     $q->td($q->textfield({-name=>"threshold",
                                           -size=>"25"}))) 
} 

sub get_general_information_input {
    my $self = shift;
    my $q = $self->cgi;
    return
               $q->Tr($q->td($q->h4("General information"))) .
               $q->Tr($q->td("Email address",
                              $self->help_link("email"), $q->br),
                      $q->td($q->textfield({-name=>"email",
                                            -value=>$self->email,
                                            -size=>"25"}))) .
               $q->Tr($q->td("Name your job"),
                      $q->td($q->textfield({-name=>"job_name",
                                            -size=>"25"}))) 
}

sub get_optional_option {
    my $self = shift;
    my $q = $self->cgi;
    return
      $q->Tr($q->td($q->a({-href=>'#',
                           -id=>'optionaltoggle',
                           -onClick=>"toggle_visibility_tbody('optional', 'optionaltoggle'); " .
                                     "return false;"},
                                     "Show optional parameters"))) .
             $q->tbody({-id=>'optional', -style=>'display:none'},
                 $q->Tr($q->td("X origin",
                                $self->help_link("origin"), $q->br),
                        $q->td($q->textfield({-name=>"x_origin",
                                              -size=>"25"}))) .
                 $q->Tr($q->td("Y origin",
                                $self->help_link("origin"), $q->br),
                        $q->td($q->textfield({-name=>"y_origin",
                                              -size=>"25"}))) .
                 $q->Tr($q->td("Z origin",
                                $self->help_link("origin"), $q->br),
                        $q->td($q->textfield({-name=>"z_origin",
                                              -size=>"25"})))
                 );

}

sub get_submit_parameter_help {
    my $self = shift;
    return [
        $self->parameter("job_name", "Job name", 1),
        $self->file_parameter("map", "Density map"),
        $self->parameter("resolution", "Resolution for the density map"),
        $self->parameter("spacing", "Spacing for the density map"),
        $self->parameter("threshold", "Threshold for the density map"),
        $self->parameter("x_origin", "X origin for the density map"),
        $self->parameter("y_origin", "Y origin for the density map"),
        $self->parameter("z_origin", "Z origin for the density map"),
        $self->file_parameter("symm_pdb", "Input PDB for symmetry case"),
        $self->parameter("cn_symmetry", "Number of Cn symmetry")
    ];
}

sub get_submit_page {
    my $self = shift;
    my $q = $self->cgi;

    my $job_name  = $q->param('job_name')||"";          # user-provided job name
    my $email     = $q->param('email')||"";             # user's e-mail
    my $input_map = $q->upload('map');                  # user-provided density map 
    my $resolution= $q->param('resolution')||"";        # user-provided resolution 
    my $spacing   = $q->param('spacing')||"";           # user-provided spacing 
    my $threshold = $q->param('threshold')||"";         # user-provided density threshold 
    my $x_origin  = $q->param('x_origin')||"0";         # user-provided x origin for map 
    my $y_origin  = $q->param('y_origin')||"0";         # user-provided y origin for map 
    my $z_origin  = $q->param('z_origin')||"0";         # user-provided z origin for map 
    my $input_symm_pdb = $q->upload('symm_pdb');        # uploaded file handle
    my $cn_symmetry = $q->param('cn_symmetry')||"1";     # user-provided number of Cn symmetry 

    if ($job_name eq "") {
        throw saliweb::frontend::InputValidationError(
                   "Job name is missing!");
    }
    if (!looks_like_number($resolution)) {
        throw saliweb::frontend::InputValidationError(
                   "Map resolution input is missing or invalid.");
    }
    if (!looks_like_number($spacing)) {
        throw saliweb::frontend::InputValidationError(
                   "Vector spacing input is missing or invalid.");
    }
    if (!looks_like_number($cn_symmetry) || $cn_symmetry < 3) {
        throw saliweb::frontend::InputValidationError(
                   "Cn symmetry should be an integer, of 3 or more.");
    }
    if (!looks_like_number($threshold)) {
        throw saliweb::frontend::InputValidationError(
                   "Contour level input is missing or invalid.");
    }
    if (!looks_like_number($x_origin) || !looks_like_number($y_origin)
        || !looks_like_number($z_origin)) {
        throw saliweb::frontend::InputValidationError(
                   "Origin input is invalid.");
    }
    if (!defined ($input_map)){
        throw saliweb::frontend::InputValidationError(
                   "Please upload input density map.");
    }
    if (!defined ($input_symm_pdb)) {
        throw saliweb::frontend::InputValidationError(
                   "Please select upload subunit PDB coordinate file.");
    }
    # Create job directory, add input files, then submit the job
    my $job = $self->make_job($job_name);
    my $jobdir = $job->directory;

    my $output_file_name = $jobdir . "/input.mrc";
    $self->write_input_map_file ($input_map, $output_file_name);
   
    $output_file_name = $jobdir . "/input.pdb";
    $self->write_input_pdb_file ($input_symm_pdb, $output_file_name);

    my $input_param = $jobdir . "/param.txt";
    open(INPARAM, "> $input_param")
       or throw saliweb::frontend::InternalError("Cannot open $input_param: $!");
    print INPARAM "$resolution\n";
    print INPARAM "$spacing\n";
    print INPARAM "$threshold\n";
    print INPARAM "$x_origin\n";
    print INPARAM "$y_origin\n";
    print INPARAM "$z_origin\n";
    print INPARAM "$cn_symmetry\n";

    close INPARAM
       or throw saliweb::frontend::InternalError("Cannot close $input_param: $!");

    $job->submit($email);

    # Inform the user of the job name and results URL
    my $return=
      $q->h1("Job Submitted") .
      $q->hr .
      $q->p("Your job " . $job->name . " has been submitted to the server." .
            "<BR> Please see the job results <a href=\"" .
            $job->results_url . "\">here</a> ");
    if ($email) {
        $return.=$q->p("<BR>You will be notified at $email when <a href=\"" .
            $job->results_url . "\">job results</a> " . "are available.");
    }

    $return .=
      $q->p("<BR>You can check on your job at the " .
            "<a href=\"" . $self->queue_url .
            "\">MultiFit current queue page</a>.").
      #$q->p("The estimated execution time is ~90 min, depending on the load.").
      $q->p("<BR>If you experience any problems or if you do not receive the results " .
            "for more than 12 hours, please <a href=\"" .
            $self->contact_url . "\">contact us</a>.") .
      $q->p("<BR>Thank you for using our server and good luck in your research!");

    return $return;
}

sub write_input_pdb_file {
    my ($self, $input_pdb_file, $output_pdb_file) = @_;

    my $file_contents = "";
    my $atoms = 0;
    while (<$input_pdb_file>) {
        if (/^ATOM  /) { $atoms++; }
        $file_contents .= $_;
    }
    if ($atoms == 0) {
        throw saliweb::frontend::InputValidationError(
                   "PDB file contains no ATOM records!");
    }
    open(INPDB, "> $output_pdb_file")
       or throw saliweb::frontend::InternalError("Cannot open $output_pdb_file: $!");
    print INPDB $file_contents;
    close INPDB
       or throw saliweb::frontend::InternalError("Cannot close $output_pdb_file: $!");
}

sub write_input_map_file {
    my ($self, $input_map_file, $output_map_file) = @_;
    my $map_contents = "";
    while (<$input_map_file>) {
        $map_contents .= $_;
    }
    open(INMAP, "> $output_map_file")
       or throw saliweb::frontend::InternalError("Cannot open $output_map_file: $!");
    print INMAP $map_contents;
    close INMAP
       or throw saliweb::frontend::InternalError("Cannot close $output_map_file: $!");
}


sub allow_file_download {
    my ($self, $file) = @_;
    return ($file eq 'multifit.output'  or $file =~ /asmb.model..*pdb/ or 
            $file eq 'multifit.log' or
            $file =~ /asmb.model..*jpg/ or $file =~ /asmb.model..*chimerax/ or 
            $file =~ /asmb.models.tar.gz/ or $file =~ /input.mrc/ or 
            $file =~ 'scores.output' or $file =~ 'dockref.output' );
}

sub get_file_mime_type {
    my ($self, $file) = @_;
    if ($file =~ /asmb.model..*chimerax/){
       return 'application/x-chimerax';
    }
    elsif ($file =~ /asmb.model..*pdb/){
       return 'chemical/x-pdb';
    }
    return 'text/plain';
}

sub get_results_page {
    my ($self, $job) = @_;
    my $q = $self->cgi;
    if (-f "multifit.output") {
        return $self->display_ok_symm_job($q, $job);
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
   my %fit_solution;
   if (! -f 'multifit.output'){
       print "multifit.output file doesn't exist.\n";
       return;
   }
   open(MULT_OUT, "< multifit.output") or die "Can't open multifit.output: $!";

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

sub display_ok_symm_job {
   my ($self, $q, $job) = @_;
   my $return= $q->p("Job '<b>" . $job->name . "</b>' has completed.");

   my %fit_solution = read_multifit_output_file();
   if (!%fit_solution){
       return $self->display_failed_job($q, $job);
   }

   my $total_solution = scalar @{$fit_solution{"solution index"}};
   my $contents = "";
   my $total_column = 5;
   my $j=0;

   for ( my $row=0; $row < ($total_solution-1)/$total_column; $row++ )
   {
     my $td = "";
     for ( my $column=0; $column < $total_column; $column++ ){
       my $cc_score = 1-$fit_solution{"fitting score"}[$j]; 
       $cc_score = sprintf ("%.3f", $cc_score);
       my $pdb_file = $fit_solution{"solution filename"}[$j];
       my (@filename) = split (/\./, $pdb_file);
       my $image_file    = "asmb.model." . $filename[2] . ".jpg"; 
       my $chimerax_file = "asmb.model." . $filename[2] . ".chimerax"; 
       my $image_url    = $job->get_results_file_url($image_file);
       my $chimerax_url = $job->get_results_file_url($chimerax_file);
       my $job_url      = $job->get_results_file_url($pdb_file);

       $td .= $q->td("<a href=\"$chimerax_url\"><img src=\"$image_url\"></img></a><br>" .
                     "<a href=\"$job_url\">" . $pdb_file . "</a><br>" .
                     "CC score=" . $cc_score);
       $j++;
     }
     $contents .= $q->Tr($td);
   }
   $return.= $q->p($q->table($contents));
 
   $return.= $q->p("<BR>Download <a href=\"" . 
          $job->get_results_file_url("multifit.output") .
          "\">multifit.output</a>, <a href=\"" .
          $job->get_results_file_url("asmb_models.tar.gz") .
          "\">asmb_models.tar.gz</a>.");

   $return .= $job->get_results_available_time();

   return $return;
}

sub display_failed_job {
    my ($self, $q, $job) = @_;
    my $return= $q->p("Your MultiFit job '<b>" . $job->name .
                      "</b>' failed to produce any output models.");
    $return.=$q->p("This is usually caused by incorrect inputs " .
                   "(e.g. corrupt PDB file, inappropriate voxel spacing or contour level).");
    #$return.=$q->p("For a discussion of some common input errors, please see the " .
    #               $q->a({-href=>$self->help_url . "#errors"}, "help page") .
    #               ".");
    $return.= $q->p("For more information, you can download the " .
                    "<a href=\"" . $job->get_results_file_url("multifit.log") .
                    "\">MultiFit log file</a>." .
                    "<BR>If the problem is not clear from this log, " .
                    "please <a href=\"" .
                    $self->contact_url . "\">contact us</a> for " .
                    "further assistance.");
    return $return;
}

1;
