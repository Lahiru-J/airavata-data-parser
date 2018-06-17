package org.airavata.datacat.helper.gaussian;

import java.io.*;
import java.util.ArrayList;

public class Distribution {

    public static String getValues(String gaussianOutputFile) throws Exception {
        //First find the method
        MethodParser pp = new MethodParser(new MethodLexer(new FileReader(gaussianOutputFile)));
        pp.parse();

        // then find the wavefunction
        WavefunctionParser pp11 = new WavefunctionParser(new WavefunctionLexer(new FileReader(gaussianOutputFile)));
        pp11.parse();

        // concatenate runtyp1  and runtype2 into runtype
        InputStream mylist1a = new FileInputStream(System.getProperty("java.io.tmpdir")
                + File.separator + DefaultGaussianParser.randomNum + "runtype1");
        InputStream mylist2a = new FileInputStream(System.getProperty("java.io.tmpdir")
                + File.separator + DefaultGaussianParser.randomNum + "runtype2");
        SequenceInputStream str4a = new SequenceInputStream(mylist1a, mylist2a);
        PrintStream temp4a = new PrintStream(new FileOutputStream(System.getProperty("java.io.tmpdir")
                + File.separator + DefaultGaussianParser.randomNum + "runtype"));

        int ccc1;
        while ((ccc1 = str4a.read()) != -1)
            temp4a.write(ccc1);

        // read the runtype file
        FileInputStream fis = new FileInputStream(System.getProperty("java.io.tmpdir")
                + File.separator + DefaultGaussianParser.randomNum + "runtype");
        DataInputStream dis = new DataInputStream(new BufferedInputStream(fis));
        String record = dis.readLine();
        String record1 = String.valueOf(new char[]{'o', 'p', 't', 'R', 'H', 'F'});
        String record1a = String.valueOf(new char[]{'o', 'p', 't', 'B', '3', 'L', 'Y', 'P'});
        String record1b = String.valueOf(new char[]{'o', 'p', 't', 'c', 'a', 's', 's', 'c', 'f'});
        String record1c = String.valueOf(new char[]{'o', 'p', 't', 'c', 'c', 's', 'd'});
        String record1d = String.valueOf(new char[]{'s', 'c', 'f', 'R', 'H', 'F'});
        String record1e = String.valueOf(new char[]{'o', 'p', 't', 'B', '3', 'P', 'W', '9', '1'});
        String record1f = String.valueOf(new char[]{'o', 'p', 't', 'B', '1', 'B', '9', '5'});
        String record3 = String.valueOf(new char[]{'h', 'f', 'o', 'p', 't'});
        String record2 = String.valueOf(new char[]{'o', 'p', 't', 'M', 'P', '2'});
        String record4 = String.valueOf(new char[]{'G', '1', 'g', 'e', 'o', 'm'});

        String record5 = String.valueOf(new char[]{'C', 'B', 'S', '-', 'Q', 'g', 'e', 'o', 'm'});

        //this is for SCF, B3LYP, B3PW91(?), MP2, CASSCF Optimization
        if (record1.equals(record) || record1a.equals(record) || record1b.equals(record)
                || record1c.equals(record) || record1e.equals(record) || record1f.equals(record)) {
            GOPTLexer scanner = new GOPTLexer(new java.io.FileReader(gaussianOutputFile));
            GOPTParser goptParser = new GOPTParser(scanner);
            goptParser.init_actions();
            goptParser.parse();

            BufferedReader reader = new BufferedReader(new FileReader(System.getProperty("java.io.tmpdir") + File.separator
                    + DefaultGaussianParser.randomNum + "temporary2"));
            String temp = reader.readLine();
            while (!temp.startsWith("DataSet:")) {
                temp = reader.readLine();
            }
            ArrayList<Double> values = new ArrayList();
            temp = reader.readLine();
            while (temp != null && !temp.isEmpty()) {
                values.add(Double.parseDouble(temp.split(",")[1].trim()));
                temp = reader.readLine();
            }

            Double[][] returnArr = new Double[4][];
            returnArr[0] = new Double[values.size()];
            for (double d = 1; d <= values.size(); d++) {
                returnArr[0][(int) d - 1] = d;
            }
            returnArr[1] = values.toArray(new Double[values.size()]);

            reader = new BufferedReader(new FileReader(System.getProperty("java.io.tmpdir") + File.separator
                    + DefaultGaussianParser.randomNum + "temporary3"));
            temp = reader.readLine();
            while (!temp.startsWith("DataSet:")) {
                temp = reader.readLine();
            }
            values = new ArrayList();
            temp = reader.readLine();
            while (temp != null && !temp.isEmpty()) {
                values.add(Double.parseDouble(temp.split(",")[1].trim()));
                temp = reader.readLine();
            }
            returnArr[2] = values.toArray(new Double[values.size()]);

            reader = new BufferedReader(new FileReader(System.getProperty("java.io.tmpdir") + File.separator
                    + DefaultGaussianParser.randomNum + "Energy_data"));
            temp = reader.readLine();
            while (!temp.startsWith("DataSet:")) {
                temp = reader.readLine();
            }
            values = new ArrayList();
            temp = reader.readLine();
            while (temp != null && !temp.isEmpty()) {
                if (temp.split(",").length == 2) {
                    try {
                        values.add(Double.parseDouble(temp.split(",")[1].trim()));
                    } catch (NumberFormatException ex) {
                        ex.printStackTrace();
                    }
                }
                temp = reader.readLine();
            }
            returnArr[3] = values.toArray(new Double[values.size()]);

            StringBuilder str = new StringBuilder();
            try {
                if (returnArr[0] != null && returnArr[0].length > 0) {
                    str.append("Iterations:").append(returnArr[0]).append(System.lineSeparator());
                }
                if (returnArr[1] != null && returnArr[1].length > 0) {
                    str.append("MaximumGradientDistribution:").append(returnArr[1]).append(System.lineSeparator());
                }
                if (returnArr[2] != null && returnArr[2].length > 0) {
                    str.append("RMSGradientDistribution:").append(returnArr[2]).append(System.lineSeparator());
                }
                if (returnArr[3] != null && returnArr[3].length > 0) {
                    str.append("EnergyDistribution:").append(returnArr[3]);
                }
            } catch (Exception ex) {
                ex.printStackTrace();
            }

            return str.toString();
        }

        return null;
    }
}
