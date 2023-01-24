package clm.jasper;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;

import com.github.javaparser.JavaParser;
import com.github.javaparser.JavaToken;
import com.github.javaparser.Range;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.comments.Comment;
import com.github.javaparser.ast.expr.AnnotationExpr;

public class Parser {
    public static JavaParser parser = new JavaParser();

    /**
     * Parse the code in the given file, will remove all the comments
     * 
     * @param filename the path to the file needs to be parsed
     * @return the root of the parsed AST
     */
    public static CompilationUnit parseFile(String filename) {
        try {
            Node root = parser.parse(new File(filename)).getResult().get();
            // removeComments(root);
            // removeAnnotation(root);
            return (CompilationUnit) root;
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * Parse the code in the given file, can choose to remove all the comments or
     * not
     * 
     * @param filename      the path to the file needs to be parsed
     * @param removeComment true for removing the comments, false for keeping the
     *                      comments
     * @return the root of the parsed AST
     */
    public static CompilationUnit parseFile(String filename, boolean removeComment) {
        try {
            Node root = parser.parse(new File(filename)).getResult().get();
            if (removeComment) {
                removeComments(root);
                removeAnnotation(root);
            }
            return (CompilationUnit) root;
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 
     * @param code
     * @param removeComment
     * @return
     */
    public static Node parseMethodDeclaration(String code, boolean removeComment) {
		try {
			Node root = parser.parseMethodDeclaration(code).getResult().get();
			if (removeComment) {
                removeComments(root);
                removeAnnotation(root);
            }
			return root;
		} catch (Exception e) {
			return null;
		}
	}

    /**
     * Remove the comments in the Java code
     * 
     * @param node parsed node representing a snippet of code
     */
    public static void removeComments(Node node) {
        node = node.removeComment();
        for (Comment comment : node.getAllContainedComments()) {
            comment.remove();
        }
        for (Node child : node.getChildNodes()) {
            removeComments(child);
        }
    }

    /**
     * 
     * @param node
     */
    public static void removeAnnotation(Node node) {
		for (Node annotation : node.findAll(AnnotationExpr.class))
			annotation.removeForced();
	}

    /**
     * Remove the empty lines in the given code
     * 
     * @param code input code
     * @return the code without empty lines
     */
    public static String removeEmptyLines(String code) {
        String[] codeLines = code.split("[\\r\\n]+");
        if (codeLines.length == 0)
            return "";
        String result = codeLines[0];
        for (int i = 1; i < codeLines.length; i += 1) {
            if (!codeLines[i].trim().equals(""))
                result += "\n" + codeLines[i];
        }
        return result;
    }

    /**
     * Build an AST where each node is an ASTNode object from the node parsed by
     * JavaParser
     * 
     * @param node  parsed node representing a snippet of code
     * @param depth the depth of the root node in the AST
     * @return the root of the built AST
     */
    public static ASTNode buildAST(Node node, int depth) {
        ASTNode astnode = new ASTNode(node, depth);
        for (Node child : node.getChildNodes()) {
            ASTNode astchild = buildAST(child, depth + 1);
            astnode.addChild(astchild);
        }
        return astnode;
    }

    /**
     * Check if a node has its corresponding source code contains the given code
     * 
     * @param node a node parsed by JavaParser
     * @param code a piece of source code
     * @return true if the node contains the given source code
     */
    public static boolean containCode(Node node, String code) {
        if (!node.getRange().isPresent())
            return false;
        String nodestring = node.toString().replaceAll("\\s+", "");
        String codestring = code.replaceAll("\\s+", "");
        return nodestring.contains(codestring);
    }

    /**
     * Check if a node has its corresponding source code contains the given code
     * that is within the given range
     * 
     * @param node      a node parsed by JavaParser
     * @param code      a piece of source code
     * @param startLine the start line of the given range of code
     * @param endLine   the end line of the given range of code (included)
     * @return true if the node contains the given source code
     */
    public static boolean containCode(Node node, String code, int startLine, int endLine) {
        if (!node.getRange().isPresent())
            return false;
        Range range = node.getRange().get();
        if (range.begin.line > startLine || range.end.line < endLine)
            return false;
        String nodestring = node.toString().replaceAll("\\s+", "");
        String codestring = code.replaceAll("\\s+", "");
        return nodestring.contains(codestring);
    }

    /**
     * Check if a node has its corresponding source code contained by the given code
     * that is within the given range
     * 
     * @param node      a node parsed by JavaParser
     * @param code      a piece of source code
     * @param startLine the start line of the given range of code
     * @param endLine   the end line of the given range of code (included)
     * @return true if the node is contained by the given source code
     */
    public static boolean containedByCode(Node node, String code, int startLine, int endLine) {
        if (!node.getRange().isPresent())
            return false;
        Range range = node.getRange().get();
        if (range.begin.line < startLine || range.end.line > endLine)
            return false;
        String nodestring = node.toString().replaceAll("\\s+", "");
        String codestring = code.replaceAll("\\s+", "");
        return codestring.contains(nodestring);
    }

    /**
     * A helper function for findNodeContainCode
     * 
     * @param node
     * @param code
     * @param startLine
     * @param endLine
     * @param result
     */
    private static void findNodeContainCode_(Node node, String code, int startLine, int endLine, Node[] result) {
        if (containCode(node, code, startLine, endLine)) {
            result[0] = node;
            List<Node> children = node.getChildNodes();
            for (Node child : children) {
                findNodeContainCode_(child, code, startLine, endLine, result);
            }
        }
    }

    /**
     * Find the smallest node that contains the given code that is within the given
     * range
     * 
     * @param node      a node parsed by JavaParser
     * @param code      a piece of source code
     * @param startLine the start line of the given range of code
     * @param endLine   the end line of the given range of code (included)
     * @return the smallest node containing the given code
     */
    public static Node findNodeContainCode(Node node, String code, int startLine, int endLine) {
        Node[] result = { null };
        findNodeContainCode_(node, code, startLine, endLine, result);
        return result[0];
    }

    /**
     * A helper function for findNodeContainedByCode
     * 
     * @param node
     * @param code
     * @param startLine
     * @param endLine
     * @param result
     */
    private static void findNodeContainedByCode_(Node node, String code, int startLine, int endLine,
            ArrayList<Node> result) {
        if (containedByCode(node, code, startLine, endLine)) {
            result.add(node);
        } else {
            for (Node child : node.getChildNodes()) {
                findNodeContainedByCode_(child, code, startLine, endLine, result);
            }
        }
    }

    /**
     * Find all the biggest nodes contained by the given piece of code
     * 
     * @param node      a node parsed by JavaParser
     * @param code      a piece of source code
     * @param startLine the start line of the given range of code
     * @param endLine   the end line of the given range of code (included)
     * @return a list of nodes contained by the given code
     */
    public static ArrayList<Node> findNodeContainedByCode(Node node, String code, int startLine, int endLine) {
        ArrayList<Node> result = new ArrayList<Node>();
        findNodeContainedByCode_(node, code, startLine, endLine, result);
        return result;
    }

    /***
     * A helper function for findNodeContainedByRange
     * 
     * @param node
     * @param startLine
     * @param startColumn
     * @param endLine
     * @param endColumn
     * @param result
     */
    private static void findNodeContainedByRange_(Node node, int startLine, int startColumn, int endLine, int endColumn,
            ArrayList<Node> result) {
        boolean covered = false;
        if (!node.getRange().isPresent())
            return;
        Range range = node.getRange().get();
        if (range.begin.line > startLine || (range.begin.line == startLine && range.begin.column >= startColumn)) {
            if (range.end.line < endLine || (range.end.line == endLine && range.end.column <= endColumn))
                covered = true;
        }
        if (covered)
            result.add(node);
        else {
            for (Node child : node.getChildNodes()) {
                findNodeContainedByRange_(child, startLine, startColumn, endLine, endColumn, result);
            }
        }
    }

    /**
     * Find all the biggest nodes contained by the given range
     * 
     * @param node        a node parsed by JavaParser
     * @param startLine   the star tline of the given range
     * @param startColumn the start column of the given range
     * @param endLine     the end line of the given range (included)
     * @param endColumn   the end column of the given range (included)
     * @return a list of nodes contained by the given range
     */
    public static ArrayList<Node> findNodeContainedByRange(Node node, int startLine, int startColumn, int endLine,
            int endColumn) {
        ArrayList<Node> result = new ArrayList<Node>();
        findNodeContainedByRange_(node, startLine, startColumn, endLine, endColumn, result);
        return result;
    }

    /**
     * A helper function for findCommonParent
     * 
     * @param node
     * @param subnodes
     * @param result
     */
    public static void findCommonParent_(Node node, ArrayList<Node> subnodes, Node[] result) {
        boolean covering = true;
        for (Node subnode : subnodes) {
            Range range = subnode.getRange().get();
            if (!node.getRange().get().contains(range)) {
                covering = false;
                break;
            }
        }
        if (covering) {
            result[0] = node;
            for (Node child : node.getChildNodes()) {
                findCommonParent_(child, subnodes, result);
            }
        }
    }

    /**
     * Find the smallest common parent of the given nodes
     * 
     * @param node     a node parsed by JavaParser
     * @param subnodes a list of nodes
     * @return the smallest common parent of the given nodes
     */
    public static Node findCommonParent(Node node, ArrayList<Node> subnodes) {
        Node[] result = { null };
        findCommonParent_(node, subnodes, result);
        return result[0];
    }

    /**
     * Get the code between [startLine, endLine] in the given file
     * 
     * @param filename  the path to the file
     * @param startLine the start line of the code
     * @param endLine   the end line of the code (included)
     * @return the code at [startLine, endLine] in the file
     * @throws Exception
     */
    public static String getCode(String filename, int startLine, int endLine) throws Exception {
        BufferedReader br = new BufferedReader(new FileReader(new File(filename)));
        String line;
        int cnt = 0;
        String code = "";
        while ((line = br.readLine()) != null) {
            cnt += 1;
            if (startLine <= cnt && cnt <= endLine)
                code += line;
            if (cnt > endLine)
                break;
        }
        br.close();
        return code;
    }

    /**
     * Get the indentation (in number of whitespace) of a given line in the given file
     * 
     * @param filename the path to the file
     * @param line the line number of the code to check indentation
     * @return the indentation of the given line
     */
    public static int getIndent(String filename, int line) {
        Node root = Parser.parseFile(filename);
        int indent = -1;
        for (JavaToken token : root.getTokenRange().get()) {
            if (token.getRange().get().begin.line != line)
                continue;
            if (token.getCategory() != JavaToken.Category.WHITESPACE_NO_EOL) {
                indent = token.getRange().get().begin.column - 1;
                break;
            }
        }
        return indent;
    }

    /**
     * Get the indentation of a given AST node
     * 
     * @param node the AST node to check indentation
     * @return the indentation of the given AST node
     */
    public static int getIndent(Node node) {
        if (! node.getTokenRange().isPresent())
            return -1;
        return node.getTokenRange().get().iterator().next().getRange().get().begin.column - 1;
    }
}
