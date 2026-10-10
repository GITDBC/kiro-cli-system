> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# MCP

> Enterprise governance of MCP servers for Kiro

By default, your users can use any MCP server in their Kiro client. As an administrator, you have the ability to either entirely disable the use of MCP servers by your users, or specify a vetted list of MCP servers that your users are allowed to use.

You control these restrictions using an MCP on/off toggle and an MCP registry attribute that are part of the [Kiro Profile](https://kiro.dev/docs/enterprise/concepts.md#kiro-profile). These profiles can be defined at an organization level or at an account level, with the account-level profile superseding the organizational-level profile. You can specify a default MCP policy for your organization and override it for specific accounts; for example, disable MCP for the organization but enable it with an allow-list for certain teams (accounts).

MCP governance applies to users authenticating with IAM Identity Center or API keys. Builder ID and social auth users are not subject to organization-level MCP controls.

**⚠️ Warning:** Both the toggle and the registry settings are enforced on the client side. As with any client-enforced configuration, they can be circumvented by users, e.g., via administrative access to their local machine.

## Disabling MCP for your organization

To disable MCP for your account or organization:
1. Open the Kiro console.
1. Choose **Settings**.
1. Under **Shared settings**, toggle **Model Context Protocol (MCP)** to **Off**.

When MCP is off, the client suppresses all MCP servers — user-configured, legacy, registry, and session-injected — and no MCP tools are available to the agent. The `/mcp` panel displays `MCP has been disabled by your administrator`.

MCP also fails closed if the client cannot reach the governance API: MCP is disabled and `/mcp` shows `Failed to retrieve MCP settings — MCP disabled`. Fail-closed events are typically transient and clear once the client reconnects to the governance API.

## Specifying an MCP allow-list for your organization

To control which MCP servers your users can access, create a JSON file with the allowed servers, serve it over HTTPS, and add the URL to your Kiro profile. Kiro clients using this profile allow users to access only the MCP servers in your allow-list.

### Specifying the MCP registry URL

1. Open the Kiro console.
1. Choose **Settings**.
1. Under **Shared settings**, ensure **Model Context Protocol (MCP)** is **On**.
1. In the **MCP Registry URL** field, choose **Edit**.
1. Enter the URL of an MCP registry JSON file containing the allow-listed MCP servers.
1. Choose **Save**.

![MCP governance settings](https://kiro.dev/images/enterprise/mcp-governance.png)

The MCP registry URL is encrypted both in transit and at rest in accordance with [our data encryption policy](https://kiro.dev/docs/privacy-and-security/data-protection.md#data-encryption).

### MCP registry file format

The format of the registry JSON file is a subset of the server schema JSON in the [MCP registry standard](https://github.com/modelcontextprotocol/registry) v0.1. The JSON schema definition for the subset supported by Kiro is available in the [registry schema](#mcp-registry-json-schema) section at the end of this document.

The following example shows an MCP registry file containing both a remote (HTTP) and a local (stdio) MCP server definition.

```json
{
  "servers": [
    {
      "server": {
        "name": "my-remote-server",
        "title": "My server",
        "description": "My server description",
        "version": "1.0.0",
        "remotes": [
          {
            "type": "streamable-http",
            "url": "https://acme.com/my-server",
            "headers": [
              {
                "name": "X-My-Header",
                "value": "SomeValue"
              }
            ]
          }
        ]
      }
    },
    {
      "server": {
        "name": "my-local-server",
        "title": "My server",
        "description": "My server description",
        "version": "1.0.0",
        "packages": [
          {
            "registryType": "npm",
            "registryBaseUrl": "https://npm.acme.com",
            "identifier": "@acme/my-server",
            "transport": {
              "type": "stdio"
            },
            "runtimeArguments": [
              {
                "type": "positional",
                "value": "-q"
              }
            ],
            "packageArguments": [
              {
                "type": "positional",
                "value": "start"
              }
            ],
            "environmentVariables": [
              {
                "name": "ENV_VAR",
                "value": "ENV_VAR_VALUE"
              }
            ]
          }
        ]
      }
    }
  ]
}
```

The following table lists the properties for the registry JSON file. All properties are mandatory, unless otherwise noted. See the [registry schema](#mcp-registry-json-schema) section for the full JSON schema.

Nested attributes appear indented from their parent. For example, "headers" is a child attribute of "remotes", and "name" and "value" are child attributes of "headers".

  
    | Attribute | Description | Optional? | Example value |
  

  
    | **Common attributes** |

    | name | Server name. Must be unique within a given registry file. |  | "aws-ccapi-mcp" |

    | title | Human-readable server name. | Yes | "AWS CC API" |

    | description | Description of server. |  | "Manage AWS infra through natural language." |

    | version | Version of server. Semantic versioning (x.y.z) is strongly recommended. |  | "1.0.2" |

    | **Remote (HTTP) server attributes** |

    | remotes | Array with exactly one entry specifying the remote endpoint. |  | - |

    | &nbsp;&nbsp;&nbsp;&nbsp;type | Must be one of "streamable-http" or "sse". |  | "streamable-http" |

    | &nbsp;&nbsp;&nbsp;&nbsp;url | MCP server endpoint URL. |  | "https://mcp.figma.com/mcp" |

    | &nbsp;&nbsp;&nbsp;&nbsp;headers | Array of HTTP headers to include in each request. | Yes | - |

    | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name | HTTP header name. |  | "Authorization" |

    | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value | HTTP header value. |  | "Bearer mF_9.B5f-4.1JqM" |

    | **Local (stdio) server attributes** |

    | packages | Array with exactly one entry containing the MCP server definition. |  | - |

    | &nbsp;&nbsp;&nbsp;&nbsp;registryType | Must be one of "npm", "pypi", or "oci".

            The following package runners are used to download and run the MCP server package:
            - For registry type "npm", the "npx" runner is used
            - For "pypi", "uvx" is used
            - For "oci", "docker" is used

            Client machines must have the appropriate package runners pre-installed. |  | “npm” |

    | &nbsp;&nbsp;&nbsp;&nbsp;registryBaseUrl | Package registry URL. | Yes | "https://npm.acme.com" |

    | &nbsp;&nbsp;&nbsp;&nbsp;identifier | Server package identifier. |  | "@acme/my-server" |

    | &nbsp;&nbsp;&nbsp;&nbsp;transport | Object with exactly one property, "type". |  | - |

    | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;type | Must be "stdio". |  | “stdio” |

    | &nbsp;&nbsp;&nbsp;&nbsp;runtimeArguments | Array of arguments provided to the runtime, that is, to npx, uvx or docker. | Yes | - |

    | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;type | Must be "positional". |  | “positional” |

    | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value | Runtime argument value. |  | “-q” |

    | &nbsp;&nbsp;&nbsp;&nbsp;packageArguments | Array of arguments provided to the MCP server. | Yes | - |

    | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;type | Must be "positional". |  | “positional” |

    | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value | Package argument value. |  | “start” |

    | &nbsp;&nbsp;&nbsp;&nbsp;environmentVariables | Array of env vars to set before starting the server. | Yes | - |

    | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name | Environment variable name. |  | "LOG_LEVEL" |

    | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value | Environment variable value. |  | “INFO” |

  

### Serving the MCP registry file

Serve the MCP registry JSON file over HTTPS using any web server, such as Amazon S3, Apache, or nginx. The URL must be accessible to Kiro clients on your users' computers but can be private to your corporate network.

The HTTPS endpoint must have a valid SSL certificate signed by a trusted Certificate Authority. Self-signed certificates are not supported.

Kiro fetches the MCP registry at startup and every 24 hours. During periodic synchronization, if a locally installed MCP server is no longer in the registry, Kiro terminates that server and prevents users from adding it back. If the locally installed server has a different version than the server in the registry, Kiro relaunches the server with the version defined in the registry.

### Overriding parameters

Registry MCP server parameters (URL, package identifier, runtimeArguments, and so forth) are read-only. However, users can:
1. Specify additional environment variables for local MCP servers.
1. Specify additional HTTP headers for remote MCP servers.
1. Change the request timeout.
1. Set the MCP server scope (Global, Workspace, or a specific Agent Configuration).
1. Set MCP tool trust permissions.

User-specified environment variables or HTTP headers override registry definitions. This allows users to specify attributes specific to their setup, such as authentication keys or local folder paths.

### MCP registry JSON schema

The following JSON schema defines the MCP registry file format supported by Kiro. You can use this schema to validate any registry files that you create.

```json
{
  "$schema": "https://json-schema.org/draft-07/schema",
  "properties": {
    "servers": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "server": {
            "$ref": "#/definitions/ServerDetail"
          }
        },
        "required": [
          "server"
        ]
      }
    }
  },
  "definitions": {
    "ServerDetail": {
      "properties": {
        "name": {
          "description": "Server name. Must be unique within a given registry file.",
          "example": "weather-mcp",
          "maxLength": 200,
          "minLength": 3,
          "pattern": "^[a-zA-Z0-9._-]+$",
          "type": "string"
        },
        "title": {
          "description": "Optional human-readable title or display name for the MCP server. MCP subregistries or clients MAY choose to use this for display purposes.",
          "example": "Weather API",
          "maxLength": 100,
          "minLength": 1,
          "type": "string"
        },
        "description": {
          "description": "Clear human-readable explanation of server functionality. Should focus on capabilities, not implementation details.",
          "example": "MCP server providing weather data and forecasts via OpenWeatherMap API",
          "maxLength": 100,
          "minLength": 1,
          "type": "string"
        },
        "version": {
          "description": "Version string for this server. SHOULD follow semantic versioning (e.g., '1.0.2', '2.1.0-alpha'). Equivalent of Implementation.version in MCP specification. Non-semantic versions are allowed but may not sort predictably. Version ranges are rejected (e.g., '^1.2.3', '~1.2.3', '\u003e=1.2.3', '1.x', '1.*').",
          "example": "1.0.2",
          "maxLength": 255,
          "type": "string"
        },
        "packages": {
          "items": {
            "$ref": "#/definitions/Package"
          },
          "type": "array",
          "minItems": 0,
          "maxItems": 1
        },
        "remotes": {
          "items": {
            "anyOf": [
              {
                "$ref": "#/definitions/StreamableHttpTransport"
              },
              {
                "$ref": "#/definitions/SseTransport"
              }
            ]
          },
          "type": "array",
          "minItems": 0,
          "maxItems": 1
        }
      },
      "required": [
        "name",
        "description",
        "version"
      ],
      "type": "object"
    },
    "Package": {
      "properties": {
        "registryType": {
          "description": "Registry type indicating how to download packages (e.g., 'npm', 'pypi', 'oci')",
          "enum": [
            "npm",
            "pypi",
            "oci"
          ],
          "type": "string"
        },
        "registryBaseUrl": {
          "description": "Base URL of the package registry",
          "examples": [
            "https://registry.npmjs.org",
            "https://pypi.org",
            "https://docker.io"
          ],
          "format": "uri",
          "type": "string"
        },
        "identifier": {
          "description": "Package identifier - either a package name (for registries) or URL (for direct downloads)",
          "examples": [
            "@modelcontextprotocol/server-brave-search",
            "https://github.com/example/releases/download/v1.0.0/package.mcpb"
          ],
          "type": "string"
        },
        "transport": {
          "anyOf": [
            {
              "$ref": "#/definitions/StdioTransport"
            },
            {
              "$ref": "#/definitions/StreamableHttpTransport"
            },
            {
              "$ref": "#/definitions/SseTransport"
            }
          ],
          "description": "Transport protocol configuration for the package"
        },

        "runtimeArguments": {
          "description": "A list of arguments to be passed to the package's runtime command (such as docker or npx).",
          "items": {
            "$ref": "#/definitions/PositionalArgument"
          },
          "type": "array"
        },
        "packageArguments": {
          "description": "A list of arguments to be passed to the package's binary.",
          "items": {
            "$ref": "#/definitions/PositionalArgument"
          },
          "type": "array"
        },
        "environmentVariables": {
          "description": "A mapping of environment variables to be set when running the package.",
          "items": {
            "$ref": "#/definitions/KeyValueInput"
          },
          "type": "array"
        }
      },
      "required": [
        "registryType",
        "identifier",
        "transport"
      ],
      "type": "object"
    },
    "StdioTransport": {
      "properties": {
        "type": {
          "description": "Transport type",
          "enum": [
            "stdio"
          ],
          "example": "stdio",
          "type": "string"
        }
      },
      "required": [
        "type"
      ],
      "type": "object"
    },
    "StreamableHttpTransport": {
      "properties": {
        "type": {
          "description": "Transport type",
          "enum": [
            "streamable-http"
          ],
          "example": "streamable-http",
          "type": "string"
        },
        "url": {
          "description": "URL template for the streamable-http transport. Variables in {curly_braces} reference argument valueHints, argument names, or environment variable names. After variable substitution, this should produce a valid URI.",
          "example": "https://api.example.com/mcp",
          "type": "string"
        },
        "headers": {
          "description": "HTTP headers to include",
          "items": {
            "$ref": "#/definitions/KeyValueInput"
          },
          "type": "array"
        }
      },
      "required": [
        "type",
        "url"
      ],
      "type": "object"
    },
    "SseTransport": {
      "properties": {
        "type": {
          "description": "Transport type",
          "enum": [
            "sse"
          ],
          "example": "sse",
          "type": "string"
        },
        "url": {
          "description": "Server-Sent Events endpoint URL",
          "example": "https://mcp-fs.example.com/sse",
          "format": "uri",
          "type": "string"
        },
        "headers": {
          "description": "HTTP headers to include",
          "items": {
            "$ref": "#/definitions/KeyValueInput"
          },
          "type": "array"
        }
      },
      "required": [
        "type",
        "url"
      ],
      "type": "object"
    },
    "PositionalArgument": {
      "properties": {
        "type": {
          "enum": [
            "positional"
          ],
          "example": "positional",
          "type": "string"
        },
        "value": {
          "description": "The value for the input.",
          "type": "string"
        }
      },
      "required": [
        "type",
        "value"
      ],
      "type": "object"
    },
    "KeyValueInput": {
      "properties": {
        "name": {
          "description": "Name of the header or environment variable.",
          "example": "SOME_VARIABLE",
          "type": "string"
        },
        "value": {
          "description": "The value for the input.",
          "type": "string"
        }
      },
      "required": [
        "name"
      ],
      "type": "object"
    }
  },
  "required": [
    "servers"
  ],
  "type": "object"
}
```
