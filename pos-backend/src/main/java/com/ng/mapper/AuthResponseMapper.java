package com.ng.mapper;

import com.ng.modal.User;
import com.ng.payload.response.AuthResponse;

public class AuthResponseMapper {

    public static AuthResponse toDto(User user, String jwt) {
        AuthResponse authResponse = new AuthResponse();
        authResponse.setJwt(jwt);
        authResponse.setUser(UserMapper.toDTO(user));

        return authResponse;
    }
}
