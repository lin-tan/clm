package clm.jasper;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Stack;

import com.github.javaparser.Range;
import com.github.javaparser.ast.Node;

public class ASTNode implements Comparable<ASTNode> {
	public Node node;
	public int depth;
	public ASTNode parent;
	public ArrayList<ASTNode> children = new ArrayList<ASTNode>();

	public ASTNode(Node node, int depth) {
		this.node = node;
		this.depth = depth;
	}

	
	/** 
	 * @param child
	 */
	public void addChild(ASTNode child) {
		this.children.add(child);
		child.addParent(this);
	}

	
	/** 
	 * @param parent
	 */
	public void addParent(ASTNode parent) {
		this.parent = parent;
	}

	
	/** 
	 * @return Range
	 */
	public Range getRange() {
		return this.node.getRange().get();
	}

	
	/** 
	 * @param clazz
	 * @return ArrayList<ASTNode>
	 */
	public ArrayList<ASTNode> getChildrenByTpye(Class<?> clazz) {
		ArrayList<ASTNode> children = new ArrayList<ASTNode>();
		for (ASTNode child : this.children) {
			if (child.node.getClass().equals(clazz)) {
				children.add(child);
			}
		}
		return children;
	}

	
	/** 
	 * @param clazz
	 * @return boolean
	 */
	public boolean classEquals(Class<?> clazz) {
		return this.node.getClass().equals(clazz);
	}

	
	/** 
	 * @return String
	 */
	public String getValue() {
		return this.node.toString();
	}

	
	/** 
	 * @return String
	 */
	public String getNodeClass() {
		String classname = this.node.getClass().toString();
		return classname.substring(classname.lastIndexOf(".") + 1);
	}

	
	/** 
	 * @param node
	 */
	public void sortChildren(ASTNode node) {
		Collections.sort(node.children);
		for (ASTNode child : node.children)
			sortChildren(child);
	}

	
	/** 
	 * @return ArrayList<ASTNode>
	 */
	public ArrayList<ASTNode> dfs() {
		sortChildren(this);

		ArrayList<ASTNode> dfs = new ArrayList<ASTNode>();
		Stack<ASTNode> stack = new Stack<ASTNode>();
		stack.push(this);
		while (!stack.isEmpty()) {
			ASTNode cur = stack.pop();
			for (int i = cur.children.size() - 1; i >= 0; i -= 1) {
				stack.push(cur.children.get(i));
			}

			dfs.add(cur);
		}
		return dfs;
	}

	public void print() {
		for (ASTNode astnode : this.dfs()) {
			System.out.println(astnode);
		}
	}

	
	/** 
	 * @return String
	 */
	public String toString() {
		return "depth: " + this.depth + ", node type: " + this.getNodeClass() + ", size: " + this.children.size() + "\n"
				+ "range: " + this.node.getRange().get().toString() + "\ncode:\n" + this.node.toString();
	}

	
	/** 
	 * @param astnode
	 * @return int
	 */
	public int compareTo(ASTNode astnode) {
		if (!this.node.getRange().isPresent())
			return 1;
		if (!astnode.node.getRange().isPresent())
			return -1;
		Range r1 = this.node.getRange().get();
		Range r2 = astnode.node.getRange().get();
		if (r1.begin.isBefore(r2.begin))
			return -1;
		else if (r1.begin.equals(r2.begin) && r1.end.isBefore(r2.end))
			return -1;
		else
			return 1;
	}
}
