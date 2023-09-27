#!/bin/bash

# Function to finish the AcTag family generation
function finish_generation() {
    ant
    if [ -f "../python/actag/generated_families/${tagFamilyName}.java" ]; # Only run generation if a tag family file was generated
    then
        # Check if the c and h files are generated, and generated them if not
        # Also regenerate if remenants of the build process are present
        if [[ ! -f "actag_files_for_apriltag/${tagFamilyName}/tag${tagFamilyName}.c" ]] || 
           [[ ! -f "actag_files_for_apriltag/${tagFamilyName}/tag${tagFamilyName}.h" ]] ||
           [[ -f "../python/actag/generated_families/${tagFamilyName}Sonar.java" ]];
        then
            echo "Generating C files...";
            mkdir actag_files_for_apriltag/;
            mkdir actag_files_for_apriltag/$tagFamilyName/;
            java -cp april.jar april.tag.TagToC april.tag.$tagFamilyName ./actag_files_for_apriltag/$tagFamilyName/;
            rm ../python/actag/generated_families/${tagFamilyName}.java
            tagFamilyNameSonar="${tagFamilyName}Sonar"
            sed -i "s/${tagFamilyNameSonar}/${tagFamilyName}/g" ../python/actag/generated_families/${tagFamilyNameSonar}.java
            mv ../python/actag/generated_families/${tagFamilyName}Sonar.java ../python/actag/generated_families/${tagFamilyName}.java
        else
            echo "C files already generated..."
        fi

        # Check if they want to generate the images... if so, do it
        if $generateimages
        then
            echo "Generating ${tagFamilyName} images..."
            java -cp april.jar april.tag.GenerateTags april.tag.$tagFamilyName ./image_files/$tagFamilyName/
        fi
        echo "Tag Family $tagFamilyName Finished!"
        exit
    else 
        echo ""
        echo "AcTag family generation failed: Generator wasn't run long enough to generate a partial AcTag family."
        exit
    fi
}

# Get command line arguments and set default parameters
databits=
minimumhammingdistance=
generateimages=false
while getopts d:h:i flag; do
    case "${flag}" in
        d) databits=${OPTARG};;
        h) minimumhammingdistance=${OPTARG};;
        i) generateimages=true;;
        :) echo "Missing option argument for -$OPTARG" >&2; exit 1;;
    esac
done

# Determine the tag family name
tagFamilyName="AcTag${databits}h$minimumhammingdistance";

# Output chosen parameters and the tag family name
echo ""
echo "===== Generating AcTag Family ====="
echo "Desired Data Bits: $databits";
echo "Minimum Hamming Distance: $minimumhammingdistance";
echo "Generate Image Files: $generateimages";
echo "Tag Family Name: $tagFamilyName";
echo "==================================="
echo ""

# Finish processing if interrupted prematurely
trap "finish_generation" INT;

# If the family isn't generated, or the C files aren't, or if 
# there's a remenant of a previous build process, generate the .java files
mkdir ../python/actag/generated_families/;
mkdir build/;
rm april.jar;
ant
if [[ ! -f "../python/actag/generated_families/${tagFamilyName}.java" ]] || 
   [[ ! -f "actag_files_for_apriltag/${tagFamilyName}/tag${tagFamilyName}.c" ]] ||
   [[ ! -f "actag_files_for_apriltag/${tagFamilyName}/tag${tagFamilyName}.h" ]] ||
   [[ -f "../python/actag/generated_families/${tagFamilyName}Sonar.java" ]];
then
    echo "Generating ${tagFamilyName}.java..."
    java -cp april.jar april.tag.TagFamilyGenerator $databits $minimumhammingdistance
    if (( $? == 0 )); # Only finish generation if the TagFamilyGenerator didn't throw an error
    then
        finish_generation
    else
        echo ""
        echo "AcTag family generation failed: See previous error"
    fi
else
    echo "${tagFamilyName}.java already generated..."
    echo "Delete the ../python/actag/generated_families/${tagFamilyName}.java file if you want to regenerate it"
    finish_generation
fi