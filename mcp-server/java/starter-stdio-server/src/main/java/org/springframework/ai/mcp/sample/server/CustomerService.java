package org.springframework.ai.mcp.sample.server;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Service;

@Service
public class CustomerService {
	@Tool(description = "Get all of customers")
	public List<Customer> getAllCustomers() {
		return List.of(
			new Customer("1", "John Doe", "john@gmail.com"),
			new Customer("2", "Jane Doe", "jane@mail.com"	),
			new Customer("3", "Sandra Mathew", "sandra@mail.com"	),
			new Customer("4", "Sibendu Das", "sdas@gmail.com")
		);	
	}

	@Tool(description = "Get a single customer by ID")
	public Customer getCustomer(@ToolParam( description =  "Customer ID") String id) {
		List<Customer> customers = getAllCustomers();
		Customer cust = null;
		for (Customer c : customers) {
			if(c.getId().equals(id)) {
				cust = c;
				break;
			}
		}
		return cust;
	}
}