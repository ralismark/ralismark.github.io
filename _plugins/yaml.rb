require "safe_yaml/load"

module YamlParse
  def yaml_parse(input)
    SafeYAML.load(input)
  end
end

Liquid::Template.register_filter(YamlParse)
