// Hộp bao vùng nổi bật (Vision saliency), chạy cục bộ. In "x y w h" gốc trên-trái, 0..1.
// Không có vùng chắc -> in 0 và thoát mã 2.
import Foundation
import Vision
import ImageIO

let args = CommandLine.arguments
guard args.count == 2 else {
    FileHandle.standardError.write("usage: saliency_box in\n".data(using: .utf8)!)
    exit(64)
}
let url = URL(fileURLWithPath: args[1])
guard let src = CGImageSourceCreateWithURL(url as CFURL, nil),
      let cg = CGImageSourceCreateImageAtIndex(src, 0, nil) else { exit(65) }
let req = VNGenerateAttentionBasedSaliencyImageRequest()
let handler = VNImageRequestHandler(cgImage: cg, options: [:])
do { try handler.perform([req]) } catch {
    FileHandle.standardError.write("\(error)\n".data(using: .utf8)!)
    exit(70)
}
guard let obs = req.results?.first as? VNSaliencyImageObservation,
      let objs = obs.salientObjects, !objs.isEmpty else {
    print("0"); exit(2)
}
let ranked = objs.sorted { $0.boundingBox.width * $0.boundingBox.height > $1.boundingBox.width * $1.boundingBox.height }
let best = ranked[0].boundingBox
let area = best.width * best.height
if area < 0.03 || area > 0.70 { print("0"); exit(2) }
if ranked.count > 1 {
    let second = ranked[1].boundingBox.width * ranked[1].boundingBox.height
    if second > area * 0.72 { print("0"); exit(2) }
}
let x = best.origin.x
let y = 1 - best.origin.y - best.height
print(String(format: "%.4f %.4f %.4f %.4f", x, y, best.width, best.height))
