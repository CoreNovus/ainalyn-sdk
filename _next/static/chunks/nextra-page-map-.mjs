import meta from "../../../pages/_meta.ts";
import v1_meta from "../../../pages/v1/_meta.ts";
import v1_advanced_meta from "../../../pages/v1/advanced/_meta.ts";
import v1_api_reference_meta from "../../../pages/v1/api-reference/_meta.ts";
import v1_concepts_meta from "../../../pages/v1/concepts/_meta.ts";
import v1_getting_started_meta from "../../../pages/v1/getting-started/_meta.ts";
import v1_guides_meta from "../../../pages/v1/guides/_meta.ts";
export const pageMap = [{
  data: meta
}, {
  name: "index",
  route: "/",
  frontMatter: {
    "sidebarTitle": "Index"
  }
}, {
  name: "v1",
  route: "/v1",
  children: [{
    data: v1_meta
  }, {
    name: "advanced",
    route: "/v1/advanced",
    children: [{
      data: v1_advanced_meta
    }, {
      name: "architecture-overview",
      route: "/v1/advanced/architecture-overview",
      frontMatter: {
        "sidebarTitle": "Architecture Overview"
      }
    }, {
      name: "compilation-flow",
      route: "/v1/advanced/compilation-flow",
      frontMatter: {
        "sidebarTitle": "Compilation Flow"
      }
    }, {
      name: "system-context",
      route: "/v1/advanced/system-context",
      frontMatter: {
        "sidebarTitle": "System Context"
      }
    }]
  }, {
    name: "api-reference",
    route: "/v1/api-reference",
    children: [{
      data: v1_api_reference_meta
    }, {
      name: "api",
      route: "/v1/api-reference/api",
      frontMatter: {
        "sidebarTitle": "API"
      }
    }, {
      name: "builders",
      route: "/v1/api-reference/builders",
      frontMatter: {
        "sidebarTitle": "Builders"
      }
    }, {
      name: "cli",
      route: "/v1/api-reference/cli",
      frontMatter: {
        "sidebarTitle": "CLI"
      }
    }, {
      name: "entities",
      route: "/v1/api-reference/entities",
      frontMatter: {
        "sidebarTitle": "Entities"
      }
    }]
  }, {
    name: "concepts",
    route: "/v1/concepts",
    children: [{
      data: v1_concepts_meta
    }, {
      name: "building-your-agent",
      route: "/v1/concepts/building-your-agent",
      frontMatter: {
        "sidebarTitle": "Building Your Agent"
      }
    }, {
      name: "how-the-sdk-works",
      route: "/v1/concepts/how-the-sdk-works",
      frontMatter: {
        "sidebarTitle": "How the Sdk Works"
      }
    }, {
      name: "what-is-an-agent",
      route: "/v1/concepts/what-is-an-agent",
      frontMatter: {
        "sidebarTitle": "What Is an Agent"
      }
    }, {
      name: "what-you-control",
      route: "/v1/concepts/what-you-control",
      frontMatter: {
        "sidebarTitle": "What You Control"
      }
    }]
  }, {
    name: "getting-started",
    route: "/v1/getting-started",
    children: [{
      data: v1_getting_started_meta
    }, {
      name: "index",
      route: "/v1/getting-started",
      frontMatter: {
        "sidebarTitle": "Index"
      }
    }, {
      name: "installation",
      route: "/v1/getting-started/installation",
      frontMatter: {
        "sidebarTitle": "Installation"
      }
    }, {
      name: "quickstart",
      route: "/v1/getting-started/quickstart",
      frontMatter: {
        "sidebarTitle": "Quickstart"
      }
    }, {
      name: "your-first-agent",
      route: "/v1/getting-started/your-first-agent",
      frontMatter: {
        "sidebarTitle": "Your First Agent"
      }
    }]
  }, {
    name: "guides",
    route: "/v1/guides",
    children: [{
      data: v1_guides_meta
    }, {
      name: "errors",
      route: "/v1/guides/errors",
      frontMatter: {
        "sidebarTitle": "Errors"
      }
    }, {
      name: "modules",
      route: "/v1/guides/modules",
      frontMatter: {
        "sidebarTitle": "Modules"
      }
    }, {
      name: "prompts",
      route: "/v1/guides/prompts",
      frontMatter: {
        "sidebarTitle": "Prompts"
      }
    }, {
      name: "tools",
      route: "/v1/guides/tools",
      frontMatter: {
        "sidebarTitle": "Tools"
      }
    }, {
      name: "validation",
      route: "/v1/guides/validation",
      frontMatter: {
        "sidebarTitle": "Validation"
      }
    }, {
      name: "workflows",
      route: "/v1/guides/workflows",
      frontMatter: {
        "sidebarTitle": "Workflows"
      }
    }, {
      name: "yaml-export",
      route: "/v1/guides/yaml-export",
      frontMatter: {
        "sidebarTitle": "Yaml Export"
      }
    }]
  }]
}];