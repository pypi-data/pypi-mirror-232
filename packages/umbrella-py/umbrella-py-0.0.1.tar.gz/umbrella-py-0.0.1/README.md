# umbrella-py 🚧

![Status](https://img.shields.io:/static/v1?label=Status&message=Under%20Construction&color=teal)

Pure Python implementation for the Umbrella project - a tool to instpect static runtime information of Objective-C and
Swift binaries. As of now, MachO and PE binaries will be accepted by the API.

**Plase follow the [documentation](https://matrixeditor.github.io/umbrella-py/) for more details on how to use this library.**

## Swift-Dump Examples

Structs can be fully reversed using the internal API. Even generic types are supported.

<table>
<thead>
  <td>Original program</td>
  <td>Re-structured with `dump_struct`</td>
</thead>
<tbody>
<tr>
<td>

```swift
struct Resolution {
    var width = 0
    var height = 0
}
struct Person<A> {
  var name: String
  let foo: A
}
```

</td>
<td>

```swift
struct main.Resolution {
  // Fields
  var width: Swift.Int
  var height: Swift.Int
}
struct main.Person<A> {
  // Fields
  var name: Swift.String
  let foo: A
}
```

</td>
</tr>
</tbody>
</table>

Classes are more complicated as they store more than just their fields. Note that generic classes won't be reversed
fully as Swift's generation of generic signatures is not
the same on all plattforms.

<table>
<thead>
  <td>Original program</td>
  <td>Re-structured with `dump_class`</td>
</thead>
<tbody>
<tr>
<td>

```swift
public class Bar {
    public func x() -> String {...}
    public func y() -> Int64 {...}
}

public class Foo: Bar {
    public let i = 0;
    var someLongVariableName = 1;
    private func indexed() -> Int {...}
    public override func x() -> String {...}
    public override func y() -> Int64 {...}
}
```

</td>
<td>

```swift
public class main.Bar {
  // Methods
  /* 0x1270 */ public func x() -> Swift.String
  /* 0x12a0 */ public func y() -> Swift.Int64
  /* 0x1320 */ static func <stripped> // Init
}
public class main.Foo: ? {
  // Properties/Fields
  let i: Swift.Int
  var someLongVariableName: Swift.Int

  // Methods
  /* 0x13a0 */ func someLongVariableName.getter : Swift.Int // (stripped)
  /* 0x13f0 */ func someLongVariableName.setter : Swift.Int // (stripped)
  /* 0x1440 */ func someLongVariableName.modify : Swift.Int // (stripped)
  /* 0x14b0 */ func <stripped> // Method
  // Overridden functions
  /* 0x14cc */ public override func x() -> Swift.String // from main.Bar
  /* 0x14fc */ public override func y() -> Swift.Int64 // from main.Bar
  /* 0x151c */ static override func <stripped> // Init from main.Bar

}
```

</td>
</tr>
</tbody>
</table>