package org.airavata.datacat.helper.gaussian;

public class DefaultGaussianParser {
    public final static int randomNum = (int) (Math.random() * 100000000);

    public static void main(String[] args) {
        try {
            // Calling the distribution
            System.out.println(Distribution.getValues(args[0]));

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
