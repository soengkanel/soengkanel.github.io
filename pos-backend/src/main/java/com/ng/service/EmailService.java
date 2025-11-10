package com.ng.service;

public interface EmailService {

    void sendEmail(String to, String subject, String body);

//    void sendResetEmail(String to, String subject, String text);
}
