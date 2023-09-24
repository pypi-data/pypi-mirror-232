"use strict";

const {
    simpleFun,
    nodehandleRunWhen,
    nodehandleQuery,
    zionNew,
    zionStartServer,
    zionObjInterface,
    zionPlay,
    zionPause,
    zionBranch,
    zionQuery,
    zionGraphStructure,
    zionRegisterCustomNodeHandle,
    zionRunCustomNodeLoop,
    graphbuilderNew,
    graphbuilderCustomNode,
    graphbuilderPromptNode,
    graphbuilderDenoCodeNode,
    graphbuilderVectorMemoryNode,
    graphbuilderCommit
} = require("./native/zion.node");

const toSnakeCase = str => str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);

const transformKeys = (obj) => {
    if (Array.isArray(obj)) {
        return obj.map(val => transformKeys(val));
    } else if (obj !== null && obj.constructor === Object) {
        return Object.keys(obj).reduce((accumulator, key) => {
            accumulator[toSnakeCase(key)] = transformKeys(obj[key]);
            return accumulator;
        }, {});
    }
    return obj;
};

class NodeHandle {
    constructor(nh) {
        this.nh = nh;
    }

    runWhen(graphBuilder, otherNodeHandle) {
        return nodehandleRunWhen.call(this.nh, graphBuilder.g, otherNodeHandle.nh);
    }

    query(branch, frame) {
        return nodehandleQuery.call(this.nh, branch, frame);
    }
}


class Zion {
    constructor(fileId, url) {
        this.chi = zionNew(fileId, url);
    }

    startServer(filePath) {
        return zionStartServer.call(this.chi, filePath);
    }

    objectInterface(executionStatus) {
        return zionObjInterface.call(this.chi, executionStatus);
    }

    play(branch, frame) {
        return zionPlay.call(this.chi, branch, frame);
    }

    pause(branch, frame) {
        return zionPause.call(this.chi, branch, frame);
    }

    query(query, branch, frame) {
        return zionQuery.call(this.chi, query, branch, frame)
    }

    branch(branch, frame) {
        return zionBranch.call(this.chi, branch, frame);
    }

    graphStructure(branch) {
        return zionGraphStructure.call(this.chi, branch);
    }

    registerCustomNodeHandle(nodeTypeName, handle) {
        // TODO: we actually pass a callback to the function provided by the user, which they invoke with their result
        return zionRegisterCustomNodeHandle.call(this.chi, nodeTypeName, handle);
    }

    runCustomNodeLoop() {
        return zionRunCustomNodeLoop.call(this.chi);
    }

}

class GraphBuilder {
    constructor() {
        this.g = graphbuilderNew();
    }

    customNode(createCustomNodeOpts) {
        return new NodeHandle(graphbuilderCustomNode.call(this.g, transformKeys(createCustomNodeOpts)));
    }

    promptNode(promptNodeCreateOpts) {
        return new NodeHandle(graphbuilderPromptNode.call(this.g, transformKeys(promptNodeCreateOpts)));
    }

    denoCodeNode(denoCodeNodeCreateOpts) {
        return new NodeHandle(graphbuilderDenoCodeNode.call(this.g, transformKeys(denoCodeNodeCreateOpts)));
    }

    vectorMemoryNode(vectorMemoryNodeCreateOpts) {
        return new NodeHandle(graphbuilderVectorMemoryNode.call(this.g, transformKeys(vectorMemoryNodeCreateOpts)));
    }

    commit(zion) {
        return graphbuilderCommit.call(this.g, zion.chi, 0);
    }
}


module.exports = {
    Zion: Zion,
    GraphBuilder: GraphBuilder,
    NodeHandle: NodeHandle,
    simpleFun: simpleFun
};