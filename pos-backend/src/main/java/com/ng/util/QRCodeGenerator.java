package com.ng.util;

import com.google.zxing.BarcodeFormat;
import com.google.zxing.EncodeHintType;
import com.google.zxing.WriterException;
import com.google.zxing.client.j2se.MatrixToImageWriter;
import com.google.zxing.common.BitMatrix;
import com.google.zxing.qrcode.QRCodeWriter;
import com.google.zxing.qrcode.decoder.ErrorCorrectionLevel;
import org.springframework.stereotype.Component;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

/**
 * Utility class for generating QR codes for table menu access
 */
@Component
public class QRCodeGenerator {

    private static final int DEFAULT_WIDTH = 300;
    private static final int DEFAULT_HEIGHT = 300;

    /**
     * Generate QR code and save to file
     *
     * @param text     The text/URL to encode
     * @param filePath Path where QR code image will be saved
     * @param width    Width of QR code
     * @param height   Height of QR code
     * @throws WriterException If QR code generation fails
     * @throws IOException     If file writing fails
     */
    public void generateQRCodeImage(String text, String filePath, int width, int height)
            throws WriterException, IOException {

        Map<EncodeHintType, Object> hints = new HashMap<>();
        hints.put(EncodeHintType.ERROR_CORRECTION, ErrorCorrectionLevel.H);
        hints.put(EncodeHintType.CHARACTER_SET, "UTF-8");
        hints.put(EncodeHintType.MARGIN, 1);

        QRCodeWriter qrCodeWriter = new QRCodeWriter();
        BitMatrix bitMatrix = qrCodeWriter.encode(text, BarcodeFormat.QR_CODE, width, height, hints);

        Path path = FileSystems.getDefault().getPath(filePath);
        MatrixToImageWriter.writeToPath(bitMatrix, "PNG", path);
    }

    /**
     * Generate QR code and return as byte array
     *
     * @param text   The text/URL to encode
     * @param width  Width of QR code
     * @param height Height of QR code
     * @return QR code image as byte array
     * @throws WriterException If QR code generation fails
     * @throws IOException     If conversion fails
     */
    public byte[] generateQRCodeBytes(String text, int width, int height)
            throws WriterException, IOException {

        Map<EncodeHintType, Object> hints = new HashMap<>();
        hints.put(EncodeHintType.ERROR_CORRECTION, ErrorCorrectionLevel.H);
        hints.put(EncodeHintType.CHARACTER_SET, "UTF-8");
        hints.put(EncodeHintType.MARGIN, 1);

        QRCodeWriter qrCodeWriter = new QRCodeWriter();
        BitMatrix bitMatrix = qrCodeWriter.encode(text, BarcodeFormat.QR_CODE, width, height, hints);

        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        MatrixToImageWriter.writeToStream(bitMatrix, "PNG", outputStream);

        return outputStream.toByteArray();
    }

    /**
     * Generate QR code with default dimensions
     *
     * @param text The text/URL to encode
     * @return QR code image as byte array
     * @throws WriterException If QR code generation fails
     * @throws IOException     If conversion fails
     */
    public byte[] generateQRCodeBytes(String text) throws WriterException, IOException {
        return generateQRCodeBytes(text, DEFAULT_WIDTH, DEFAULT_HEIGHT);
    }

    /**
     * Generate eMenu URL for a specific table
     *
     * @param baseUrl    Base URL of the application (e.g., http://yourapp.com)
     * @param branchId   Branch ID
     * @param tableId    Table ID
     * @param tableToken Secure token for table
     * @return Complete eMenu URL
     */
    public String generateMenuUrl(String baseUrl, Long branchId, Long tableId, String tableToken) {
        return String.format("%s/emenu?branch=%d&table=%d&token=%s",
                baseUrl, branchId, tableId, tableToken);
    }

    /**
     * Generate a secure token for table access
     *
     * @param branchId Branch ID
     * @param tableId  Table ID
     * @return Secure token
     */
    public String generateTableToken(Long branchId, Long tableId) {
        String raw = branchId + "-" + tableId + "-" + System.currentTimeMillis();
        return java.util.Base64.getEncoder()
                .encodeToString(raw.getBytes())
                .replaceAll("[^A-Za-z0-9]", "")
                .substring(0, 32);
    }
}
