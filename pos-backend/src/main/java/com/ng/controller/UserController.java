package com.ng.controller;

import com.ng.configrations.JwtProvider;

import com.ng.domain.UserRole;
import com.ng.exception.UserException;
import com.ng.mapper.UserMapper;
import com.ng.modal.User;

import com.ng.payload.dto.UserDTO;
import com.ng.repository.UserRepository;
import com.ng.service.UserService;
import com.ng.service.impl.CustomUserImplementation;

import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Set;


@RestController
@RequiredArgsConstructor
public class UserController {


	private final UserRepository userRepository;
	private final PasswordEncoder passwordEncoder;
	private final JwtProvider jwtProvider;
	private final CustomUserImplementation customUserImplementation;
	private final UserService userService;

	

	
	@GetMapping("/api/users/profile")
	public ResponseEntity<UserDTO> getUserProfileFromJwtHandler(
			@RequestHeader("Authorization") String jwt) throws UserException {
		User user = userService.getUserFromJwtToken(jwt);
		UserDTO userDTO=UserMapper.toDTO(user);

		return new ResponseEntity<>(userDTO,HttpStatus.OK);
	}

	@GetMapping("/api/users/customer")
	public ResponseEntity<Set<UserDTO>> getCustomerList(
			@RequestHeader("Authorization") String jwt) throws UserException {
		Set<User> users = userService.getUserByRole(UserRole.ROLE_CUSTOMER);
		Set<UserDTO> userDTO=UserMapper.toDTOSet(users);

		return new ResponseEntity<>(userDTO,HttpStatus.OK);
	}

	@GetMapping("/api/users/cashier")
	public ResponseEntity<Set<UserDTO>> getCashierList(
			@RequestHeader("Authorization") String jwt) throws UserException {
		Set<User> users = userService.getUserByRole(UserRole.ROLE_BRANCH_CASHIER);
		Set<UserDTO> userDTO=UserMapper.toDTOSet(users);

		return new ResponseEntity<>(userDTO,HttpStatus.OK);
	}

	@GetMapping("/users/list")
	public ResponseEntity<List<User>> getUsersListHandler(
			@RequestHeader("Authorization") String jwt) throws UserException {
		List<User> users = userService.getUsers();

		return new ResponseEntity<>(users,HttpStatus.OK);
	}

	@GetMapping("/users/{userId}")
	public ResponseEntity<UserDTO> getUserByIdHandler(
			@PathVariable Long userId
	) throws UserException {
		User user = userService.getUserById(userId);
		UserDTO userDTO=UserMapper.toDTO(user);

		return new ResponseEntity<>(userDTO,HttpStatus.OK);
	}







	
//	@PatchMapping("/users")
//	public ResponseEntity<User> updateUserDetailsHandler(@RequestBody
//			UpdateUserDto updatedData,
//			@RequestHeader("Authorization") String jwt) throws UserException {
//		User user = userService.getUserFromJwtToken(jwt);
//		User updatedUser = userService.updateUser(updatedData, user);
//		return ResponseEntity.ok(updatedUser);
//	}

//	@PostMapping("/auth/forgot-password")
//	public ResponseEntity<Response> sendOtpToForogotPasswordHandler(@RequestBody ForgotPasswordDto req) throws UserException, MessagingException {
//		User user = userRepository.findByEmail(req.getEmail());
//		if(user == null) {
//			throw new UserException("user not found with email " + req.getEmail());
//		}
//		String generatedOtp = userService.sendForgotPasswordOtp(req.getEmail());
//		Response response = new Response();
//		response.setMessage("Otp sent to your email successfully ");
//
//		return ResponseEntity.ok(response);
//	}

//	@PostMapping("/auth/verify-forgot-password-otp")
//	public ResponseEntity<Response> verifyForgotPasswordOtpHandler(@RequestBody VerifyForgotPasswordOtpDto req) throws Exception {
//		User user = userService.verifyForgotPasswordOtp(req.getOtp(), req.getNewPassword());
//		Response response = new Response();
//		response.setMessage("Password updated successfully ");
//		return ResponseEntity.ok(response);
//	}


}
