import rospy	
import pid

GAS_DENSITY = 2.858
ONE_MPH = 0.44704


class Controller(object):
    def __init__(self, vehicle_mass, wheel_radius, decel_limit, accel_limit, max_steer_angle):
        
        self.vehicle_mass = vehicle_mass
        self.decel_limit = decel_limit
        self.accel_limit = accel_limit
        self.wheel_radius = wheel_radius
        self.throttle_limit = 0.9
        self.start_time = rospy.get_time()
        self.steering_tol = max_steer_angle
        self.steering = pid.PID(kp = 5, ki = 0.0001, kd = .75, mn = -self.steering_tol, mx = self.steering_tol)

    def control(self, current_velocity, target_velocity, cte, dbw_enabled):

    	if dbw_enabled is False:
    		self.steering.reset()

    	# Convert to MPH
    	target_velocity = ONE_MPH * target_velocity

    	# Braking Torque 
        force = self.vehicle_mass * self.decel_limit
        torque = force * self.wheel_radius

        # Difference in Target and Actual Velocities
        del_vel = (target_velocity - current_velocity)


        # If Positive difference throttle = nonzero, brake = 0
        # Else throttle = 0, brake = nonzero
        if(del_vel > 0) and (current_velocity < target_velocity):
        	throttle = self.throttle_limit*(1.0 - (current_velocity/target_velocity))
        	brake = 0
        else:
        	throttle = 0
        	brake = torque


        curr_time = rospy.get_time()
        del_time = curr_time - self.start_time
        self.start_time = curr_time

        if(del_time == 0):
        	del_time += 0.01

        steering =  self.steering.step(cte, del_time)

        return throttle, brake, steering
