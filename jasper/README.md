# Jasper: Java AST-based Parser for Program Repair
<img src="logo.jpg" width="300" height="300" />

This is a Java static analysis tool for preprocessing data for program repair project (or potentially other projects). This offers functionalities such as

* Given the Java file and the start line and end line of a piece of code, extracting the surrounding function (keeps code format) of the code piece.
* Given the Java file and the start line and end line of a piece of code, extracting the surrounding function part before the given code piece (keeps code format).
* Given the Java file and the start line and end line of a piece of code, extracting the surrounding function part after the given code piece (keeps code format).

With these functionalities, it is easy to do more, such as

* Finding a function and replacing some lines with other code.
* Finding a function and inserting code.
* Finding a function and inserting natural language comments.

## Generate Input for CodeT5
The CodeT5InputParser defined in codet5 package offers the functionality to generate input for codet5 model. Currently, two configurations of inputs are already supported, which is included in the CodeT5Config enumeration.

Generating input for other models (PlBart, CodeGen and InCoder) are similar.

## Use in Command Line
To compile the project, run
```
javac -cp ".:lib/*" -d target src/main/java/clm/jasper/*.java src/main/java/clm/codet5/*.java src/main/java/clm/codegen/*.java src/main/java/clm/plbart/*.java src/main/java/clm/incoder/*.java src/main/java/clm/finetuning/*.java
```
To generate input for a given bug, run
```
java -cp .:target:lib/* clm.[plbart|codet5|codegen|incoder].[PlBartInputParser|CodeT5InputParser|CodeGenInputParser|InCoderInputParser] buggy_file_path buggy_line_start_loc buggy_lin_end_loc config output_file_path
```
Running the following example 
```
java -cp .:target:lib/* clm.codet5.CodeT5InputParser src/test/java/clm/Test1.java 21 21 CODET5_BASE_CODEFORM_MASKFORM_NOCOMMENT output.json
```
will get a json file named "output.json", which should contains
```
{"input":"void add(int m) {\n    System.out.println(\"before\");   \n    <extra_id_0>\n    System.out.println(\"after\");  \n}"}
```

## Use in Python Code
In additional to running in the command line, you can also call the command in Python with subprocess library. Below is an example piece of python code
```
subprocess.Popen(['java', '-cp', '.:target:lib/*', 'clm.codet5.CodeT5InputParser', 'src/test/java/clm/Test1.java', '21', '21', 'CODET5_BASE_CODEFORM_MASKFORM_NOCOMMENT', 'output.json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
```
which will do the same thing that write the input for codet5 model to output.json, and then you can write python code to read the result file and get the input.

## Develop Jasper
Jasper is mostly built on [JavaParser-3.15.14](https://javadoc.io/doc/com.github.javaparser/javaparser-core/3.15.14/index.html), you can use JavaParser to develop further functionalities.
