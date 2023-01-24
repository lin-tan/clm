package clm;

/**
 * A test class
 */
public class Test1 {
    int n;

    Test1(int n) {
        this.n = n;
    }

    /**
     * Add m to n
     * 
     * @param m
     */
    void add(int m) {
        // a test comment for empty line
        System.out.println("before");   // this is buggy function before
        this.n -= m;
        this.n /= m;
        System.out.println("after");  // this is buggy function after
    }
}
