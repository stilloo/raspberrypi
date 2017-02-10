<?php

if ($_SERVER['REQUEST_METHOD'] == 'POST')
{

  	$data = file_get_contents("php://input");

	//Removes all 3 types of line breaks
	$data = str_replace("\r", " ", $data);
	$data = str_replace("\n", " ", $data);  

	$result = json_decode($data, true);

	$myfile = fopen("readSMStest.txt", "w") or die("Unable to open file!");
	fwrite($myfile, $data);


	$strText = "SMS received from " . $result['contact'];
	fwrite($myfile,"\n" . $strText );
	fclose($myfile);

	$strCommand = "sudo /home/pi/Documents/speech.sh" . " " .  $strText ; 

	exec($strCommand, $command_output);

	foreach($command_output as $line) :

		echo $line  ;

	endforeach;

}

?>
