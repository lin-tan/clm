package clm.jasper;

import com.github.javadocparser.TokenMgrError;
import com.github.javaparser.JavaToken;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;

public class ContextParser extends Parser {

	/**
	 * A helper function for findSUrroundingFunction
	 * 
	 * @param node
	 * @param code
	 * @param startLine
	 * @param endLine
	 * @param result
	 */
	private static void getSurroundingFunction_(Node node, String code, int startLine, int endLine, Node[] result) {
		if (containCode(node, code, startLine, endLine)) {
			if (node.getClass().equals(MethodDeclaration.class) || node.getClass().equals(ConstructorDeclaration.class))
				result[0] = node;
			for (Node child : node.getChildNodes()) {
				getSurroundingFunction_(child, code, startLine, endLine, result);
			}
		}
	}

	/**
	 * Find the surrounding function of the given code
	 * 
	 * @param node      a node parsed by JavaParser, in which we find the
	 *                  surrounding function
	 * @param code      the code for which we find the surrounding function
	 * @param startLine the start line of the code
	 * @param endLine   the end line of the code (included)
	 * @return the surrounding function in String
	 */
	public static String getSurroundingFunction(Node node, String code, int startLine, int endLine) {
		Node[] result = { null };
		getSurroundingFunction_(node, code, startLine, endLine, result);
		return result[0] == null ? null : result[0].toString();
	}

	/**
	 * Find the surrounding function of the given code
	 * 
	 * @param filename  the filename, in which we find the surrounding function
	 * @param startLine the start line of the code
	 * @param endLine   the end line of the code (included)
	 * @param removeComment remove the comments or not
	 * @return the surrounding function in String
	 * @throws Exception
	 */
	public static String getSurroundingFunction(String filename, int startLine, int endLine, boolean removeComment)
			throws Exception {
		try {
			String code = getCode(filename, startLine, endLine);
			Node root = Parser.parseFile(filename, removeComment);
			return getSurroundingFunction(root, code, startLine, endLine);
		} catch (TokenMgrError e) {
			return null;
		}
	}

	/**
	 * Find the AST node of surrounding function of the gtiven code
	 * 
	 * @param filename  the filename, in which we find the surrounding function
	 * @param startLine the start line of the code
	 * @param endLine   the end line of the code (included)
	 * @param removeComment remove the comments or not
	 * @return the AST node (JavaParser Node) of the surrounding function of the given code
	 * @throws Exception
	 */
	public static Node getSurroundingFunctionNode(String filename, int startLine, int endLine, boolean removeComment) throws Exception {
		try {
			String code = getCode(filename, startLine, endLine);
			Node root = Parser.parseFile(filename, removeComment);
			Node[] result = { null };
			getSurroundingFunction_(root, code, startLine, endLine, result);
			return result[0];
		} catch (TokenMgrError e) {
			return null;
		}
	}

	/**
	 * find the surrounding function code that before the given range (not include the range)
	 * 
	 * @param filename the filename of the code
	 * @param startLine the start line of the given range
	 * @param endLine the end line of the given range
	 * @param removeComment remove the comments or not
	 * @return the surrounding function code that before the given range
	 * @throws Exception
	 */
	public static String getSurroundingFunctionBefore(String filename, int startLine, int endLine,
			boolean removeComment) throws Exception {
		try {
			String code = getCode(filename, startLine, endLine);
			Node root = Parser.parseFile(filename, removeComment);
			Node[] result = { null };
			getSurroundingFunction_(root, code, startLine, endLine, result);
			if (result[0] == null)
				return null;
			String function = "";
			int functionLine = -1;
			int functionColumn = -1;
			for (JavaToken token : result[0].getTokenRange().get()) {
				if (functionLine < 0) {
					functionLine = token.getRange().get().begin.line;
					functionColumn = token.getRange().get().begin.column;
				}
				if (token.getRange().get().end.line >= startLine)
					break;
				if (token.getCategory() == JavaToken.Category.WHITESPACE_NO_EOL &&
						token.getRange().get().begin.line > functionLine &&
						token.getRange().get().end.column < functionColumn)
					continue;
				if ((!removeComment) || (removeComment && token.getCategory() != JavaToken.Category.COMMENT))
					function += token.getText();
			}
			return function;
		} catch (TokenMgrError e) {
			return null;
		}
	}

	/**
	 * find the surrounding function code that after the given range (not include the range)
	 * 
	 * @param filename the filename of the code
	 * @param startLine the start line of the given range
	 * @param endLine the end line of the given range
	 * @param removeComment remove the comments or not
	 * @return the surrounding function code that before the given range
	 * @throws Exception
	 */
	public static String getSurroundingFunctionAfter(String filename, int startLine, int endLine, boolean removeComment) throws Exception {
		try {
			String code = getCode(filename, startLine, endLine);
			Node root = Parser.parseFile(filename, removeComment);
			Node[] result = { null };
			getSurroundingFunction_(root, code, startLine, endLine, result);
			if (result[0] == null)
				return null;
			String function = "";
			int functionLine = -1;
			int functionColumn = -1;
			for (JavaToken token : result[0].getTokenRange().get()) {
				if (functionLine < 0) {
					functionLine = token.getRange().get().begin.line;
					functionColumn = token.getRange().get().begin.column;
				}
				if (token.getRange().get().end.line <= endLine)
					continue;
				if (token.getCategory() == JavaToken.Category.WHITESPACE_NO_EOL &&
						token.getRange().get().begin.line > functionLine &&
						token.getRange().get().end.column < functionColumn)
					continue;
				if ((!removeComment) || (removeComment && token.getCategory() != JavaToken.Category.COMMENT))
					function += token.getText();
			}
			return function;
		} catch (TokenMgrError e) {
			return null;
		}
	}

	/**
	 * Similar to Parser.getCode, both function can get the code between [startLine, endLine] in the given,
	 * but this function will dedent the code based on the indentation of the surrounding function.
	 * E.g., if the surrounding function has indentation of 4 whitespaces, and code you want has indentation of 12 whitespaces.
	 * the returned code of this function will only has indentation of 8 whitespaces, while the returned code of getCode will keep all the indentation.
	 * This is useful when you want to dedent the surrounding function (typically a function signature has indentation of 4 whitespaces, 
	 * but you want to dedent the entire function).
	 * 
	 * @param filename the filename of the code
	 * @param startLine the start line of the given range
	 * @param endLine the end line of the given range (included)
	 * @param removeComment remove the comments or not
	 * @return the dedented code in range [startLine, endLine]
	 * @throws Exception
	 */
	public static String getDedentedCode(String filename, int startLine, int endLine, boolean removeComment) throws Exception {
		try{
			String code = getCode(filename, startLine, endLine);
			Node root = Parser.parseFile(filename, removeComment);
			Node[] result = { null };
			getSurroundingFunction_(root, code, startLine, endLine, result);
			if (result[0] == null)
				return null;
			String dedented = "";
			int functionLine = -1;
			int functionColumn = -1;
			for (JavaToken token : result[0].getTokenRange().get()) {
				if (functionLine < 0) {
					functionLine = token.getRange().get().begin.line;
					functionColumn = token.getRange().get().begin.column;
				}
				if (token.getRange().get().end.line < startLine)
					continue;
				if (token.getRange().get().end.line > endLine)
					break;
				if (token.getCategory() == JavaToken.Category.WHITESPACE_NO_EOL &&
						token.getRange().get().begin.line > functionLine &&
						token.getRange().get().end.column < functionColumn)
					continue;
				if ((!removeComment) || (removeComment && token.getCategory() != JavaToken.Category.COMMENT))
					dedented += token.getText();
			}
			return dedented;
		} catch (TokenMgrError e) {
			return null;
		}
	}

}
