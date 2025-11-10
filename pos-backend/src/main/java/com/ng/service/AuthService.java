package com.ng.service;

import com.ng.exception.UserException;
import com.ng.payload.dto.UserDTO;
import com.ng.payload.response.AuthResponse;

public interface AuthService {
    AuthResponse login(String username, String password) throws UserException;
    AuthResponse signup(UserDTO req) throws UserException;

    void createPasswordResetToken(String email) throws UserException;
    void resetPassword(String token, String newPassword);
}
