#!/bin/env perl

#	If <enableXXSupport> is set to true counts as a repo type for XX being NuGet, Gems, Npm, Bower, Debian, Pypi, Docker, Vagrant, and GitLfs,
#	If <calculateYumMetadata> is true on a local repository that counts as a Yum repo
#	If the repo is virtual and either <yumGroupFileNames> isn't empty or <yumRootDepth> isn't zero, it's a Yum repo
#	If it is a remote repo and <enableVcsSupport> is true, but <enableBowerSupport> isn't, then it counts as a VCS repo. This is a special case because if something has both of those checked, they don't actually conflict, and Bower takes precedence.
#	If it's a remote repo, if <p2Support> is true, then it counts as a p2 repo
#	If it's a virtual repo, if there's a <p2><enabled>true</enabled></p2>, then it counts as a p2 repo

open(CD, "<$ARGV[0]") or die("cannot open $ARGV[0]");
my $in;
my $repo;
my @pt;
my $error=0;
my $remote=0;
my $virtual=0;
my $verbose=1;
while (<CD>){
 chomp();
 if ($in){
     if ($_ =~ /<key>([^<]+)/){
   $repo=$1;
  }
  elsif ($_ =~ /<\/localRepository>|<\/remoteRepository>|<\/virtualRepository>/){
   if ($#pt>0){   
    $error++;
    printf("NOT OK: %s (%s)\n", $repo, join(",", @pt));
   }
   elsif($verbose){
    printf("OK: %s\n", $repo);
   }
   $in=$remote=$virtual=0;
   @pt=();
  }
  elsif ($_ =~ /<enable(.+)Support>true/){
   push(@pt,$1);
  }
  elsif ($_ =~ /<calculateYumMetadata>true/){
   push(@pt,"Yum");
  }
  elsif ($_ =~ /<p2Support>true|<p2><enabled>true/){
   push(@pt,"p2");
  }
 }
 elsif ($_ =~ /<localRepository>/){
  $in=1;
  @pt=();
 }
 elsif ($_ =~ /<remoteRepository>/){
  $in=1;
  $remote=1;
  @pt=();
 }
 elsif ($_ =~ /<virtualRepository>/){
  $in=1;
  $virtual=1;
  @pt=();
 }
}
close(CD);
printf("\n%s\n", ($error?"ERROR":"OK"));
exit($error);
